"""
Channel Management for Clawdbot-Python
Manages multiple communication channels (WhatsApp, Telegram, Discord, etc.)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod

from src.core.config import Settings


class BaseChannel(ABC):
    """Abstract base class for all communication channels"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        self.channel_id = channel_id
        self.config = config
        self.logger = logging.getLogger(f"channels.{channel_id}")
        self.is_running = False
        
    @abstractmethod
    async def start(self):
        """Start the channel"""
        pass
        
    @abstractmethod
    async def stop(self):
        """Stop the channel"""
        pass
        
    @abstractmethod
    async def send_message(self, recipient_id: str, message: str, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message through this channel"""
        pass
        
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the channel"""
        pass


class MockChannel(BaseChannel):
    """Mock channel for testing and development"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.message_queue = []
        self.recipients = set()
        
    async def start(self):
        """Start the mock channel"""
        self.logger.info(f"Starting mock channel: {self.channel_id}")
        self.is_running = True
        
    async def stop(self):
        """Stop the mock channel"""
        self.logger.info(f"Stopping mock channel: {self.channel_id}")
        self.is_running = False
        
    async def send_message(self, recipient_id: str, message: str, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message through the mock channel"""
        self.recipients.add(recipient_id)
        
        message_obj = {
            'id': f"msg_{datetime.now().timestamp()}",
            'recipient_id': recipient_id,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'channel_id': self.channel_id,
            'extra': extra_data or {}
        }
        
        self.message_queue.append(message_obj)
        
        # Keep queue size reasonable
        if len(self.message_queue) > 100:
            self.message_queue = self.message_queue[-50:]
            
        self.logger.debug(f"Mock sent message to {recipient_id}: {message[:50]}...")
        
        return {
            'success': True,
            'message_id': message_obj['id'],
            'sent_at': message_obj['timestamp'],
            'channel': self.channel_id
        }
        
    async def get_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from the mock channel"""
        return self.message_queue[-limit:]
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock channel"""
        return {
            'status': 'healthy',
            'channel_id': self.channel_id,
            'is_running': self.is_running,
            'message_count': len(self.message_queue),
            'recipients_count': len(self.recipients),
            'timestamp': datetime.now().isoformat()
        }


class WhatsAppChannel(BaseChannel):
    """WhatsApp channel implementation (placeholder)"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.client = None
        
    async def start(self):
        """Start WhatsApp channel (placeholder)"""
        self.logger.info(f"Starting WhatsApp channel: {self.channel_id}")
        # In real implementation, would connect to WhatsApp Business API or similar
        self.is_running = True
        
    async def stop(self):
        """Stop WhatsApp channel (placeholder)"""
        self.logger.info(f"Stopping WhatsApp channel: {self.channel_id}")
        self.is_running = False
        
    async def send_message(self, recipient_id: str, message: str, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message via WhatsApp (placeholder)"""
        # Placeholder implementation
        self.logger.debug(f"Would send WhatsApp message to {recipient_id}: {message[:50]}...")
        
        return {
            'success': True,
            'message_id': f"wa_msg_{datetime.now().timestamp()}",
            'sent_at': datetime.now().isoformat(),
            'channel': self.channel_id,
            'recipient': recipient_id
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check for WhatsApp channel"""
        return {
            'status': 'healthy',  # Placeholder
            'channel_id': self.channel_id,
            'is_running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }


class TelegramChannel(BaseChannel):
    """Telegram channel implementation (placeholder)"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.bot_token = config.get('bot_token')
        self.webhook_url = config.get('webhook_url')
        
    async def start(self):
        """Start Telegram channel (placeholder)"""
        self.logger.info(f"Starting Telegram channel: {self.channel_id}")
        # In real implementation, would set up bot webhook or polling
        self.is_running = True
        
    async def stop(self):
        """Stop Telegram channel (placeholder)"""
        self.logger.info(f"Stopping Telegram channel: {self.channel_id}")
        self.is_running = False
        
    async def send_message(self, recipient_id: str, message: str, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message via Telegram (placeholder)"""
        # Placeholder implementation
        self.logger.debug(f"Would send Telegram message to {recipient_id}: {message[:50]}...")
        
        return {
            'success': True,
            'message_id': f"tg_msg_{datetime.now().timestamp()}",
            'sent_at': datetime.now().isoformat(),
            'channel': self.channel_id,
            'recipient': recipient_id
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Telegram channel"""
        return {
            'status': 'healthy',  # Placeholder
            'channel_id': self.channel_id,
            'is_running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }


class DiscordChannel(BaseChannel):
    """Discord channel implementation (placeholder)"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.bot_token = config.get('bot_token')
        
    async def start(self):
        """Start Discord channel (placeholder)"""
        self.logger.info(f"Starting Discord channel: {self.channel_id}")
        # In real implementation, would connect to Discord API
        self.is_running = True
        
    async def stop(self):
        """Stop Discord channel (placeholder)"""
        self.logger.info(f"Stopping Discord channel: {self.channel_id}")
        self.is_running = False
        
    async def send_message(self, recipient_id: str, message: str, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message via Discord (placeholder)"""
        # Placeholder implementation
        self.logger.debug(f"Would send Discord message to {recipient_id}: {message[:50]}...")
        
        return {
            'success': True,
            'message_id': f"dc_msg_{datetime.now().timestamp()}",
            'sent_at': datetime.now().isoformat(),
            'channel': self.channel_id,
            'recipient': recipient_id
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Discord channel"""
        return {
            'status': 'healthy',  # Placeholder
            'channel_id': self.channel_id,
            'is_running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }


class ChannelManager:
    """Manages multiple communication channels"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Channel storage
        self.channels: Dict[str, BaseChannel] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, List[Callable]] = {
            'pre_receive': [],
            'post_receive': [],
            'pre_send': [],
            'post_send': []
        }
        
        # Enabled channels from settings
        self.enabled_channels = settings.enabled_channels
        
    async def initialize(self):
        """Initialize all configured channels"""
        self.logger.info("Initializing Channel Manager...")
        
        # Create and start configured channels
        for channel_type in self.enabled_channels:
            await self.create_channel(channel_type)
            
        # Add mock channel for testing
        await self.create_channel('mock')
        
        self.logger.info(f"Channel Manager initialized with {len(self.channels)} channels")
        
    async def create_channel(self, channel_type: str) -> Optional[BaseChannel]:
        """Create a new channel of the specified type"""
        channel_id = f"{channel_type}_channel_{len(self.channels)}"
        
        # Default configuration
        config = {
            'type': channel_type,
            'enabled': True,
            'rate_limit': 30,  # messages per minute
            'timeout': 30  # seconds
        }
        
        # Create appropriate channel instance
        if channel_type == 'whatsapp':
            channel = WhatsAppChannel(channel_id, config)
        elif channel_type == 'telegram':
            channel = TelegramChannel(channel_id, config)
        elif channel_type == 'discord':
            channel = DiscordChannel(channel_id, config)
        else:
            # Default to mock channel for unknown types or for testing
            channel = MockChannel(channel_id, config)
            
        # Store the channel
        self.channels[channel_id] = channel
        
        # Start the channel
        await channel.start()
        
        self.logger.info(f"Created and started channel: {channel_id}")
        
        return channel
        
    async def get_channel(self, channel_id: str) -> Optional[BaseChannel]:
        """Get a channel by ID"""
        return self.channels.get(channel_id)
        
    async def send_message(self, channel_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message through a specific channel"""
        channel = await self.get_channel(channel_id)
        
        if not channel:
            self.logger.error(f"Channel not found: {channel_id}")
            return {
                'success': False,
                'error': f'Channel {channel_id} not found',
                'timestamp': datetime.now().isoformat()
            }
            
        # Apply pre-send handlers
        processed_message = message_data.copy()
        for handler in self.message_handlers['pre_send']:
            try:
                processed_message = await handler(processed_message)
            except Exception as e:
                self.logger.error(f"Error in pre-send handler: {str(e)}")
                
        # Extract message content and recipient
        recipient_id = processed_message.get('recipient_id') or processed_message.get('user_id', 'unknown')
        message_text = processed_message.get('text', processed_message.get('message', ''))
        
        # Send the message
        result = await channel.send_message(recipient_id, message_text, extra_data=processed_message)
        
        # Apply post-send handlers
        for handler in self.message_handlers['post_send']:
            try:
                await handler(result)
            except Exception as e:
                self.logger.error(f"Error in post-send handler: {str(e)}")
                
        return result
        
    async def broadcast_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to all active channels"""
        results = {}
        
        for channel_id, channel in self.channels.items():
            if channel.is_running:
                try:
                    result = await self.send_message(channel_id, message_data)
                    results[channel_id] = result
                except Exception as e:
                    results[channel_id] = {
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.logger.error(f"Error broadcasting to channel {channel_id}: {str(e)}")
                    
        return results
        
    async def start_listening(self):
        """Start listening for incoming messages on all channels"""
        self.logger.info("Starting to listen on all channels...")
        
        start_tasks = []
        for channel_id, channel in self.channels.items():
            start_tasks.append(channel.start())
            
        await asyncio.gather(*start_tasks, return_exceptions=True)
        
        self.logger.info("All channels are now listening")
        
    async def stop_listening(self):
        """Stop listening on all channels"""
        self.logger.info("Stopping listening on all channels...")
        
        stop_tasks = []
        for channel_id, channel in self.channels.items():
            stop_tasks.append(channel.stop())
            
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        self.logger.info("All channels have stopped listening")
        
    async def register_message_handler(self, event_type: str, handler: Callable):
        """Register a message handler for specific events"""
        if event_type not in self.message_handlers:
            self.message_handlers[event_type] = []
            
        self.message_handlers[event_type].append(handler)
        self.logger.debug(f"Registered {event_type} handler")
        
    async def list_channels(self) -> List[str]:
        """List all available channel IDs"""
        return list(self.channels.keys())
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all channels"""
        channel_statuses = {}
        
        for channel_id, channel in self.channels.items():
            try:
                status = await channel.health_check()
                channel_statuses[channel_id] = status
            except Exception as e:
                channel_statuses[channel_id] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.error(f"Health check failed for channel {channel_id}: {str(e)}")
                
        return {
            'status': 'healthy',
            'channel_count': len(self.channels),
            'channels': channel_statuses,
            'enabled_channels': self.enabled_channels,
            'timestamp': datetime.now().isoformat()
        }
        
    async def shutdown(self):
        """Shutdown all channels"""
        self.logger.info("Shutting down Channel Manager...")
        
        # Stop all channels
        stop_tasks = []
        for channel in self.channels.values():
            stop_tasks.append(channel.stop())
            
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            
        # Clear channel list
        self.channels.clear()
        
        self.logger.info("Channel Manager shutdown completed")