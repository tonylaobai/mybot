"""
Agent Management for Clawdbot-Python
Manages AI agents, their configurations, and message processing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

from src.core.config import Settings
from src.tools.registry import ToolRegistry
from src.memory.manager import MemoryManager


class Agent:
    """Individual AI agent with its own configuration and capabilities"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any], tool_registry: ToolRegistry):
        self.id = agent_id
        self.config = config
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(f"agents.{agent_id}")
        self.created_at = datetime.now()
        
        # Agent state
        self.is_running = False
        self.last_activity = None
        
    async def initialize(self):
        """Initialize the agent"""
        self.logger.info(f"Initializing agent {self.id}")
        self.is_running = True
        self.last_activity = datetime.now()
        
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message and return a response"""
        self.last_activity = datetime.now()
        
        # Extract message content
        message_content = message_data.get('content', '')
        channel = message_data.get('channel', 'unknown')
        user_id = message_data.get('user_id', 'unknown')
        
        self.logger.debug(f"Processing message from {user_id} via {channel}: {message_content[:50]}...")
        
        # In a real implementation, this would call an LLM API
        # For now, we'll simulate a response
        response_content = await self._generate_response(message_content, message_data)
        
        response = {
            'agent_id': self.id,
            'response': response_content,
            'timestamp': datetime.now().isoformat(),
            'original_request': message_data
        }
        
        return response
        
    async def _generate_response(self, input_text: str, message_data: Dict[str, Any]) -> str:
        """Generate a response to the input text"""
        # This is a placeholder implementation
        # In a real system, this would call an LLM with proper prompting
        
        lower_input = input_text.lower()
        
        if 'hello' in lower_input or 'hi' in lower_input or 'hey' in lower_input:
            return f"Hello there! I'm an AI agent powered by Clawdbot-Python. How can I assist you today?"
        elif 'help' in lower_input:
            return ("I'm an AI assistant. I can help with various tasks using my tools. "
                   "Try asking me to read a file, execute a command, or search the web.")
        elif 'time' in lower_input or 'date' in lower_input:
            return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC."
        elif 'name' in lower_input:
            return f"I'm an AI agent powered by Clawdbot-Python, running with ID {self.id}."
        else:
            # For more complex queries, indicate capability to use tools
            return (f"I received your message: '{input_text}'. "
                   f"I'm an AI agent capable of using various tools. "
                   f"I can read files, execute safe commands, search the web, and more. "
                   f"What would you like me to help you with?")
                   
    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with given arguments"""
        if not self.tool_registry:
            return {
                'success': False,
                'error': 'Tool registry not available'
            }
            
        # Execute the tool through the registry
        result = await self.tool_registry.execute_tool(tool_name, **tool_args)
        
        return {
            'success': result.success,
            'result': result.result,
            'error': result.error
        }
        
    async def shutdown(self):
        """Shutdown the agent"""
        self.logger.info(f"Shutting down agent {self.id}")
        self.is_running = False


class AgentManager:
    """Manages multiple AI agents"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Agent storage
        self.agents: Dict[str, Agent] = {}
        self.default_agent_id: Optional[str] = None
        
        # Configuration
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self, tool_registry: ToolRegistry):
        """Initialize the agent manager and create default agents"""
        self.logger.info("Initializing Agent Manager...")
        
        # Set up default agent configuration
        default_config = {
            'id': 'default-agent',
            'name': 'Default Agent',
            'model': self.settings.default_model,
            'capabilities': self.settings.enabled_tools,
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        # Create default agent
        default_agent = Agent('default-agent', default_config, tool_registry)
        await default_agent.initialize()
        self.agents['default-agent'] = default_agent
        self.default_agent_id = 'default-agent'
        
        self.logger.info(f"Created default agent: {self.default_agent_id}")
        
        # If there are additional agent configs, create those too
        await self._create_additional_agents(tool_registry)
        
        self.logger.info(f"Agent Manager initialized with {len(self.agents)} agents")
        
    async def _create_additional_agents(self, tool_registry: ToolRegistry):
        """Create additional agents based on configuration"""
        # For now, just create a secondary agent as example
        # In a real system, this would read from configuration
        secondary_config = {
            'id': 'secondary-agent',
            'name': 'Secondary Agent',
            'model': self.settings.fallback_models[0] if self.settings.fallback_models else 'gpt-3.5-turbo',
            'capabilities': self.settings.enabled_tools,
            'temperature': 0.5,
            'max_tokens': 500
        }
        
        secondary_agent = Agent('secondary-agent', secondary_config, tool_registry)
        await secondary_agent.initialize()
        self.agents['secondary-agent'] = secondary_agent
        
        self.logger.info("Created secondary agent")
        
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
        
    async def get_default_agent(self) -> Optional[Agent]:
        """Get the default agent"""
        if self.default_agent_id:
            return await self.get_agent(self.default_agent_id)
        return None
        
    async def get_default_agent_id(self) -> Optional[str]:
        """Get the default agent ID"""
        return self.default_agent_id
        
    async def create_agent(self, agent_config: Dict[str, Any], tool_registry: ToolRegistry) -> Agent:
        """Create a new agent with the given configuration"""
        agent_id = agent_config.get('id', f"agent_{datetime.now().timestamp()}")
        
        # Validate configuration
        if 'name' not in agent_config:
            agent_config['name'] = f"Agent-{agent_id}"
            
        if 'model' not in agent_config:
            agent_config['model'] = self.settings.default_model
            
        if 'capabilities' not in agent_config:
            agent_config['capabilities'] = self.settings.enabled_tools
            
        # Create and initialize agent
        agent = Agent(agent_id, agent_config, tool_registry)
        await agent.initialize()
        
        # Store the agent
        self.agents[agent_id] = agent
        
        self.logger.info(f"Created new agent: {agent_id}")
        
        return agent
        
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent by ID"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.shutdown()
            del self.agents[agent_id]
            self.logger.info(f"Removed agent: {agent_id}")
            return True
        return False
        
    async def list_agents(self) -> List[str]:
        """List all available agent IDs"""
        return list(self.agents.keys())
        
    async def process_message_for_user(self, user_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message for a specific user (select appropriate agent)"""
        # For now, use the default agent
        # In a real system, this might select different agents based on user preferences,
        # message type, load balancing, etc.
        agent = await self.get_default_agent()
        
        if not agent:
            return {
                'error': 'No available agents',
                'timestamp': datetime.now().isoformat()
            }
            
        return await agent.process_message(message_data)
        
    async def broadcast_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to all agents"""
        results = {}
        
        for agent_id, agent in self.agents.items():
            try:
                result = await agent.process_message(message_data)
                results[agent_id] = result
            except Exception as e:
                results[agent_id] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.error(f"Error broadcasting to agent {agent_id}: {str(e)}")
                
        return results
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent system"""
        agent_statuses = {}
        
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = {
                'running': agent.is_running,
                'last_activity': agent.last_activity.isoformat() if agent.last_activity else None,
                'uptime': str(datetime.now() - agent.created_at) if agent.created_at else 'N/A'
            }
            
        return {
            'status': 'healthy',
            'agent_count': len(self.agents),
            'default_agent': self.default_agent_id,
            'agents': agent_statuses,
            'timestamp': datetime.now().isoformat()
        }
        
    async def shutdown(self):
        """Shutdown all agents"""
        self.logger.info("Shutting down Agent Manager...")
        
        # Shutdown all agents concurrently
        shutdown_tasks = []
        for agent in self.agents.values():
            shutdown_tasks.append(agent.shutdown())
            
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
        # Clear agent list
        self.agents.clear()
        
        self.logger.info("Agent Manager shutdown completed")