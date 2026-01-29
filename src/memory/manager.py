"""
Memory Management for Clawdbot-Python
Handles persistent storage, conversation history, and long-term memory
"""

import asyncio
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import aiosqlite
import logging


@dataclass
class Interaction:
    """Represents a single interaction between user and agent"""
    id: str
    timestamp: datetime
    source: str  # Channel where interaction occurred
    user_id: str  # User identifier
    input_text: str  # User's input
    output_text: str  # Agent's response
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass
class MemoryEntry:
    """Generic memory entry for long-term storage"""
    id: str
    timestamp: datetime
    category: str  # 'fact', 'preference', 'experience', etc.
    content: str
    tags: List[str]
    importance: float = 0.5  # 0.0 to 1.0 scale
    expires_at: Optional[datetime] = None


class MemoryManager:
    """Manages all memory-related operations"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(settings.memory_dir) / "memory.db"
        self.interactions_dir = Path(settings.memory_dir) / "interactions"
        self.daily_notes_dir = Path(settings.memory_dir) / "daily"
        
        # Ensure directories exist
        self.interactions_dir.mkdir(parents=True, exist_ok=True)
        self.daily_notes_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for recent interactions
        self._interaction_cache: Dict[str, Interaction] = {}
        self._memory_cache: Dict[str, MemoryEntry] = {}
        
    async def initialize(self):
        """Initialize the memory manager and database"""
        self.logger.info(f"Initializing memory manager with database: {self.db_path}")
        
        # Create database tables
        await self._create_tables()
        
        # Load recent entries into cache
        await self._load_recent_to_cache()
        
        self.logger.info("Memory manager initialized successfully")
        
    async def _create_tables(self):
        """Create necessary database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Interactions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    metadata TEXT,
                    session_id TEXT
                )
            ''')
            
            # Memory entries table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    importance REAL DEFAULT 0.5,
                    expires_at TEXT
                )
            ''')
            
            # Indexes for performance
            await db.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions(timestamp)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON interactions(user_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_source ON interactions(source)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_category ON memory_entries(category)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance)')
            
            await db.commit()
            
    async def _load_recent_to_cache(self):
        """Load recent interactions and memory entries into cache"""
        # Load recent interactions (last 100)
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT id, timestamp, source, user_id, input_text, output_text, metadata, session_id
                FROM interactions
                ORDER BY timestamp DESC
                LIMIT 100
            ''') as cursor:
                async for row in cursor:
                    interaction = Interaction(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        source=row[2],
                        user_id=row[3],
                        input_text=row[4],
                        output_text=row[5],
                        metadata=json.loads(row[6]) if row[6] else None,
                        session_id=row[7]
                    )
                    self._interaction_cache[interaction.id] = interaction
                    
        # Load important memory entries
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT id, timestamp, category, content, tags, importance, expires_at
                FROM memory_entries
                WHERE importance > 0.7 OR expires_at IS NULL
                ORDER BY importance DESC, timestamp DESC
                LIMIT 50
            ''') as cursor:
                async for row in cursor:
                    memory_entry = MemoryEntry(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        category=row[2],
                        content=row[3],
                        tags=json.loads(row[4]) if row[4] else [],
                        importance=row[5],
                        expires_at=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    self._memory_cache[memory_entry.id] = memory_entry
                    
    async def store_interaction(self, interaction_data: Dict[str, Any]):
        """Store an interaction in memory"""
        try:
            interaction = Interaction(
                id=interaction_data.get('id', f"int_{datetime.now().timestamp()}"),
                timestamp=interaction_data.get('timestamp', datetime.now()),
                source=interaction_data.get('source', 'unknown'),
                user_id=interaction_data.get('user_id', 'unknown'),
                input_text=interaction_data.get('input_text', ''),
                output_text=interaction_data.get('output_text', ''),
                metadata=interaction_data.get('metadata'),
                session_id=interaction_data.get('session_id')
            )
            
            # Store in database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO interactions 
                    (id, timestamp, source, user_id, input_text, output_text, metadata, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.id,
                    interaction.timestamp.isoformat(),
                    interaction.source,
                    interaction.user_id,
                    interaction.input_text,
                    interaction.output_text,
                    json.dumps(interaction.metadata) if interaction.metadata else None,
                    interaction.session_id
                ))
                await db.commit()
                
            # Add to cache
            self._interaction_cache[interaction.id] = interaction
            
            # Maintain cache size
            if len(self._interaction_cache) > 100:
                # Remove oldest entries
                sorted_ids = sorted(
                    self._interaction_cache.keys(),
                    key=lambda x: self._interaction_cache[x].timestamp
                )
                while len(self._interaction_cache) > 100:
                    oldest_id = sorted_ids.pop(0)
                    del self._interaction_cache[oldest_id]
                    
            self.logger.debug(f"Stored interaction: {interaction.id}")
            
        except Exception as e:
            self.logger.error(f"Error storing interaction: {str(e)}")
            raise
            
    async def store_memory(self, memory_data: Dict[str, Any]):
        """Store a memory entry"""
        try:
            memory_entry = MemoryEntry(
                id=memory_data.get('id', f"mem_{datetime.now().timestamp()}"),
                timestamp=memory_data.get('timestamp', datetime.now()),
                category=memory_data.get('category', 'general'),
                content=memory_data.get('content', ''),
                tags=memory_data.get('tags', []),
                importance=memory_data.get('importance', 0.5),
                expires_at=memory_data.get('expires_at')
            )
            
            # Store in database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO memory_entries
                    (id, timestamp, category, content, tags, importance, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory_entry.id,
                    memory_entry.timestamp.isoformat(),
                    memory_entry.category,
                    memory_entry.content,
                    json.dumps(memory_entry.tags),
                    memory_entry.importance,
                    memory_entry.expires_at.isoformat() if memory_entry.expires_at else None
                ))
                await db.commit()
                
            # Add to cache if important
            if memory_entry.importance > 0.7:
                self._memory_cache[memory_entry.id] = memory_entry
                
            self.logger.debug(f"Stored memory entry: {memory_entry.id} (category: {memory_entry.category})")
            
        except Exception as e:
            self.logger.error(f"Error storing memory: {str(e)}")
            raise
            
    async def get_recent_interactions(self, user_id: str = None, limit: int = 10) -> List[Interaction]:
        """Get recent interactions, optionally filtered by user"""
        interactions = []
        
        if user_id:
            # Query database for user-specific interactions
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT id, timestamp, source, user_id, input_text, output_text, metadata, session_id
                    FROM interactions
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit)) as cursor:
                    async for row in cursor:
                        interaction = Interaction(
                            id=row[0],
                            timestamp=datetime.fromisoformat(row[1]),
                            source=row[2],
                            user_id=row[3],
                            input_text=row[4],
                            output_text=row[5],
                            metadata=json.loads(row[6]) if row[6] else None,
                            session_id=row[7]
                        )
                        interactions.append(interaction)
        else:
            # Get most recent interactions from cache and database
            # First get from cache
            cached = [
                self._interaction_cache[k] for k in 
                sorted(self._interaction_cache.keys(), 
                       key=lambda x: self._interaction_cache[x].timestamp, reverse=True)[:limit]
            ]
            
            # Fill remaining from database if needed
            remaining = limit - len(cached)
            if remaining > 0:
                async with aiosqlite.connect(self.db_path) as db:
                    async with db.execute('''
                        SELECT id, timestamp, source, user_id, input_text, output_text, metadata, session_id
                        FROM interactions
                        WHERE id NOT IN ({})
                        ORDER BY timestamp DESC
                        LIMIT ?
                    '''.format(','.join(['?' for _ in cached])), (*[i.id for i in cached], remaining)) as cursor:
                        async for row in cursor:
                            interaction = Interaction(
                                id=row[0],
                                timestamp=datetime.fromisoformat(row[1]),
                                source=row[2],
                                user_id=row[3],
                                input_text=row[4],
                                output_text=row[5],
                                metadata=json.loads(row[6]) if row[6] else None,
                                session_id=row[7]
                            )
                            interactions.append(interaction)
                            
            interactions.extend(cached)
            # Sort by timestamp and take top 'limit'
            interactions.sort(key=lambda x: x.timestamp, reverse=True)
            interactions = interactions[:limit]
            
        return interactions
        
    async def search_memory(self, query: str, category: str = None, limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries based on query"""
        results = []
        
        # First search in cache for high-importance items
        for entry in self._memory_cache.values():
            if category and entry.category != category:
                continue
            if query.lower() in entry.content.lower() or query.lower() in ' '.join(entry.tags).lower():
                results.append(entry)
                
        # Then search in database
        placeholders = ['?', '?']
        params = [f'%{query}%', f'%{query}%']
        sql = '''
            SELECT id, timestamp, category, content, tags, importance, expires_at
            FROM memory_entries
            WHERE (content LIKE ? OR tags LIKE ?)
        '''
        
        if category:
            sql += ' AND category = ?'
            placeholders.append('?')
            params.append(category)
            
        sql += ' ORDER BY importance DESC, timestamp DESC LIMIT ?'
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql, params) as cursor:
                async for row in cursor:
                    memory_entry = MemoryEntry(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        category=row[2],
                        content=row[3],
                        tags=json.loads(row[4]) if row[4] else [],
                        importance=row[5],
                        expires_at=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    # Avoid duplicates with cache results
                    if not any(r.id == memory_entry.id for r in results):
                        results.append(memory_entry)
                        
        # Sort by relevance (importance first, then recency) and limit
        results.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        return results[:limit]
        
    async def get_daily_note(self, date: datetime = None) -> str:
        """Get daily notes for a specific date"""
        if date is None:
            date = datetime.now()
            
        date_str = date.strftime("%Y-%m-%d")
        note_path = self.daily_notes_dir / f"{date_str}.md"
        
        if note_path.exists():
            async with aiofiles.open(note_path, 'r', encoding='utf-8') as f:
                return await f.read()
        else:
            return f"# Daily Notes for {date_str}\n\n"
            
    async def save_daily_note(self, content: str, date: datetime = None):
        """Save daily notes for a specific date"""
        if date is None:
            date = datetime.now()
            
        date_str = date.strftime("%Y-%m-%d")
        note_path = self.daily_notes_dir / f"{date_str}.md"
        
        async with aiofiles.open(note_path, 'w', encoding='utf-8') as f:
            await f.write(content)
            
    async def cleanup_expired_entries(self):
        """Remove expired memory entries"""
        now = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Find expired entries
            async with db.execute('''
                SELECT id FROM memory_entries 
                WHERE expires_at IS NOT NULL AND datetime(expires_at) < datetime(?)
            ''', (now.isoformat(),)) as cursor:
                expired_ids = [row[0] async for row in cursor]
                
            # Delete expired entries
            if expired_ids:
                placeholders = ','.join(['?' for _ in expired_ids])
                await db.execute(f'DELETE FROM memory_entries WHERE id IN ({placeholders})', expired_ids)
                
                # Remove from cache
                for exp_id in expired_ids:
                    self._memory_cache.pop(exp_id, None)
                    
                await db.commit()
                self.logger.info(f"Cleaned up {len(expired_ids)} expired memory entries")
                
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on memory system"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Count total interactions
                async with db.execute('SELECT COUNT(*) FROM interactions') as cursor:
                    interaction_count = (await cursor.fetchone())[0]
                    
                # Count total memory entries
                async with db.execute('SELECT COUNT(*) FROM memory_entries') as cursor:
                    memory_count = (await cursor.fetchone())[0]
                    
            return {
                "status": "healthy",
                "database_path": str(self.db_path),
                "interactions_count": interaction_count,
                "memory_entries_count": memory_count,
                "cache_size": len(self._interaction_cache) + len(self._memory_cache),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Memory health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    async def close(self):
        """Close the memory manager and release resources"""
        self.logger.info("Closing memory manager")
        # Clear caches
        self._interaction_cache.clear()
        self._memory_cache.clear()