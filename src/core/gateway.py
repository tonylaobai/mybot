"""
Core Gateway component for Clawdbot-Python
Manages communication between components and coordinates system operation
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path

from src.core.config import Settings
from src.channels.manager import ChannelManager
from src.agents.manager import AgentManager
from src.memory.manager import MemoryManager


class Gateway:
    """
    Core Gateway class that coordinates all system components
    Handles message routing, component orchestration, and system lifecycle
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Component references (will be set during initialization)
        self.channel_manager: Optional[ChannelManager] = None
        self.agent_manager: Optional[AgentManager] = None
        self.memory_manager: Optional[MemoryManager] = None
        
        # System state
        self.initialized = False
        self.running = False
        
        # Message routing table
        self.routing_table: Dict[str, Callable] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, list] = {
            'message_received': [],
            'message_processed': [],
            'agent_response': [],
            'error_occurred': []
        }
        
    async def initialize(
        self, 
        channel_manager: ChannelManager, 
        agent_manager: AgentManager, 
        memory_manager: MemoryManager
    ):
        """Initialize the gateway with component managers"""
        self.logger.info("Initializing Gateway...")
        
        self.channel_manager = channel_manager
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        
        # Register message handlers
        await self._setup_message_routing()
        
        # Setup event handlers
        await self._setup_event_handlers()
        
        self.initialized = True
        self.logger.info("Gateway initialized successfully")
        
    async def _setup_message_routing(self):
        """Setup message routing between channels and agents"""
        # Register routing functions
        self.routing_table['channel_to_agent'] = self._route_channel_to_agent
        self.routing_table['agent_to_channel'] = self._route_agent_to_channel
        self.routing_table['internal_message'] = self._route_internal_message
        
        self.logger.debug("Message routing setup completed")
        
    async def _setup_event_handlers(self):
        """Setup system event handlers"""
        # Add default handlers
        self.event_handlers['message_received'].append(self._handle_message_received)
        self.event_handlers['message_processed'].append(self._handle_message_processed)
        self.event_handlers['agent_response'].append(self._handle_agent_response)
        self.event_handlers['error_occurred'].append(self._handle_error_occurred)
        
        self.logger.debug("Event handlers setup completed")
        
    async def start(self):
        """Start the gateway"""
        if not self.initialized:
            raise RuntimeError("Gateway not initialized. Call initialize() first.")
            
        self.logger.info("Starting Gateway...")
        self.running = True
        
        # Start listening on channels
        if self.channel_manager:
            await self.channel_manager.start_listening()
            
        self.logger.info("Gateway started successfully")
        
    async def stop(self):
        """Stop the gateway"""
        self.logger.info("Stopping Gateway...")
        self.running = False
        
        # Stop channel listening
        if self.channel_manager:
            await self.channel_manager.stop_listening()
            
        self.logger.info("Gateway stopped")
        
    async def shutdown(self):
        """Gracefully shutdown the gateway"""
        self.logger.info("Shutting down Gateway...")
        
        # Stop the gateway
        await self.stop()
        
        # Cleanup resources
        await self._cleanup_resources()
        
        self.logger.info("Gateway shutdown completed")
        
    async def _cleanup_resources(self):
        """Cleanup gateway resources"""
        # Clear routing table
        self.routing_table.clear()
        
        # Clear event handlers
        for key in self.event_handlers:
            self.event_handlers[key].clear()
            
        # Remove component references
        self.channel_manager = None
        self.agent_manager = None
        self.memory_manager = None
        
    async def route_message(self, source: str, destination: str, message_data: Dict[str, Any]):
        """Route a message from source to destination"""
        if not self.running:
            raise RuntimeError("Gateway is not running")
            
        route_key = f"{source}_to_{destination}"
        
        if route_key not in self.routing_table:
            self.logger.warning(f"No route found for {route_key}")
            return None
            
        # Emit message received event
        await self._emit_event('message_received', {
            'source': source,
            'destination': destination,
            'message_data': message_data,
            'timestamp': datetime.now()
        })
        
        # Route the message
        handler = self.routing_table[route_key]
        result = await handler(message_data)
        
        # Emit message processed event
        await self._emit_event('message_processed', {
            'source': source,
            'destination': destination,
            'message_data': message_data,
            'result': result,
            'timestamp': datetime.now()
        })
        
        return result
        
    async def _route_channel_to_agent(self, message_data: Dict[str, Any]):
        """Route message from channel to appropriate agent"""
        try:
            # Determine which agent should handle this message
            agent_id = await self._select_agent_for_message(message_data)
            
            if not agent_id:
                self.logger.warning("No suitable agent found for message")
                return None
                
            # Get the agent
            agent = await self.agent_manager.get_agent(agent_id)
            if not agent:
                self.logger.error(f"Agent {agent_id} not found")
                return None
                
            # Process the message with the agent
            response = await agent.process_message(message_data)
            
            # Store interaction in memory
            if self.memory_manager:
                await self.memory_manager.store_interaction({
                    'type': 'channel_to_agent',
                    'source': message_data.get('channel'),
                    'agent_id': agent_id,
                    'input': message_data,
                    'output': response,
                    'timestamp': datetime.now().isoformat()
                })
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error routing channel to agent: {str(e)}")
            await self._emit_event('error_occurred', {
                'error': str(e),
                'context': 'channel_to_agent_routing',
                'timestamp': datetime.now()
            })
            raise
            
    async def _route_agent_to_channel(self, message_data: Dict[str, Any]):
        """Route message from agent to appropriate channel"""
        try:
            # Extract channel information from message data
            channel_id = message_data.get('channel_id')
            if not channel_id:
                self.logger.error("No channel_id specified for agent to channel routing")
                return None
                
            # Send message through the channel
            if self.channel_manager:
                result = await self.channel_manager.send_message(channel_id, message_data)
                
                # Emit agent response event
                await self._emit_event('agent_response', {
                    'channel_id': channel_id,
                    'response': message_data,
                    'result': result,
                    'timestamp': datetime.now()
                })
                
                return result
            else:
                self.logger.error("Channel manager not available")
                return None
                
        except Exception as e:
            self.logger.error(f"Error routing agent to channel: {str(e)}")
            await self._emit_event('error_occurred', {
                'error': str(e),
                'context': 'agent_to_channel_routing',
                'timestamp': datetime.now()
            })
            raise
            
    async def _route_internal_message(self, message_data: Dict[str, Any]):
        """Route internal system messages"""
        # Handle internal system messages
        message_type = message_data.get('type')
        
        if message_type == 'system_notification':
            # Process system notification
            return await self._handle_system_notification(message_data)
        elif message_type == 'component_health_check':
            # Process health check
            return await self._perform_health_check()
        else:
            self.logger.warning(f"Unknown internal message type: {message_type}")
            return None
            
    async def _select_agent_for_message(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Select the appropriate agent for a given message"""
        # Simple selection logic - in a real system this would be more sophisticated
        channel = message_data.get('channel', 'unknown')
        
        # For now, return the default agent
        # In a real implementation, this would consider message content, 
        # user preferences, agent capabilities, etc.
        return await self.agent_manager.get_default_agent_id()
        
    async def _handle_system_notification(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system notifications"""
        notification_type = message_data.get('notification_type')
        self.logger.info(f"Handling system notification: {notification_type}")
        
        # Process the notification based on type
        if notification_type == 'startup':
            return {'status': 'processed', 'message': 'Startup notification handled'}
        elif notification_type == 'shutdown':
            return {'status': 'processed', 'message': 'Shutdown notification handled'}
        elif notification_type == 'health_check':
            return await self.health_check()
        else:
            return {'status': 'processed', 'message': f'Notification {notification_type} handled'}
            
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            'gateway': 'healthy' if self.running else 'stopped',
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # Check component health
        if self.channel_manager:
            health_status['components']['channel_manager'] = await self.channel_manager.health_check()
            
        if self.agent_manager:
            health_status['components']['agent_manager'] = await self.agent_manager.health_check()
            
        if self.memory_manager:
            health_status['components']['memory_manager'] = await self.memory_manager.health_check()
            
        return health_status
        
    async def health_check(self) -> Dict[str, Any]:
        """Return system health status"""
        return await self._perform_health_check()
        
    async def _handle_message_received(self, event_data: Dict[str, Any]):
        """Default handler for message received events"""
        self.logger.debug(f"Message received: {event_data.get('source')} -> {event_data.get('destination')}")
        
    async def _handle_message_processed(self, event_data: Dict[str, Any]):
        """Default handler for message processed events"""
        self.logger.debug(f"Message processed: {event_data.get('source')} -> {event_data.get('destination')}")
        
    async def _handle_agent_response(self, event_data: Dict[str, Any]):
        """Default handler for agent response events"""
        self.logger.debug(f"Agent response sent to channel: {event_data.get('channel_id')}")
        
    async def _handle_error_occurred(self, event_data: Dict[str, Any]):
        """Default handler for error occurred events"""
        self.logger.error(f"Error occurred in {event_data.get('context')}: {event_data.get('error')}")
        
    async def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit an event to all registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {str(e)}")
                    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register a new event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(handler)
        
    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove an event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass  # Handler not found