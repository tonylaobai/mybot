"""
Clawdbot-Python - A multi-channel AI assistant gateway
Main application entry point
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI
from uvicorn import Config, Server

from src.core.gateway import Gateway
from src.core.config import Settings
from src.channels.manager import ChannelManager
from src.agents.manager import AgentManager
from src.tools.registry import ToolRegistry
from src.memory.manager import MemoryManager


class ClawdbotApp:
    """
    Main Clawdbot application class
    Orchestrates all components of the system
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.app = FastAPI(
            title="Clawdbot-Python",
            description="A multi-channel AI assistant gateway",
            version="0.1.0"
        )
        
        # Initialize core components
        self.gateway = Gateway(settings)
        self.channel_manager = ChannelManager(settings)
        self.agent_manager = AgentManager(settings)
        self.tool_registry = ToolRegistry()
        self.memory_manager = MemoryManager(settings)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=self.settings.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Clawdbot-Python...")
        
        # Initialize memory manager first
        await self.memory_manager.initialize()
        
        # Register tools
        self._register_tools()
        
        # Initialize agents
        await self.agent_manager.initialize(self.tool_registry)
        
        # Initialize channels
        await self.channel_manager.initialize()
        
        # Initialize gateway
        await self.gateway.initialize(
            channel_manager=self.channel_manager,
            agent_manager=self.agent_manager,
            memory_manager=self.memory_manager
        )
        
        # Setup API routes
        self._setup_routes()
        
        self.logger.info("Clawdbot-Python initialized successfully")
        
    def _register_tools(self):
        """Register all available tools"""
        # Register built-in tools
        from src.tools.builtin import (
            ReadFileTool, WriteFileTool, ExecTool, WebSearchTool,
            BrowserTool, MessageTool, GatewayTool, SessionsTool
        )
        
        tools = [
            ReadFileTool(),
            WriteFileTool(),
            ExecTool(),
            WebSearchTool(),
            BrowserTool(),
            MessageTool(),
            GatewayTool(),
            SessionsTool()
        ]
        
        for tool in tools:
            self.tool_registry.register(tool)
            
    def _setup_routes(self):
        """Setup API routes"""
        from src.api.gateway import router as gateway_router
        from src.api.channels import router as channels_router
        from src.api.agents import router as agents_router
        from src.api.tools import router as tools_router
        
        self.app.include_router(gateway_router, prefix="/api/v1/gateway", tags=["gateway"])
        self.app.include_router(channels_router, prefix="/api/v1/channels", tags=["channels"])
        self.app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
        self.app.include_router(tools_router, prefix="/api/v1/tools", tags=["tools"])
        
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the FastAPI server"""
        config = Config(
            app=self.app,
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
        server = Server(config)
        
        # Initialize the application
        await self.initialize()
        
        # Start the server
        self.logger.info(f"Starting Clawdbot-Python server on {host}:{port}")
        await server.serve()
        
    async def shutdown(self):
        """Gracefully shutdown the application"""
        self.logger.info("Shutting down Clawdbot-Python...")
        await self.gateway.shutdown()
        await self.channel_manager.shutdown()
        await self.agent_manager.shutdown()
        await self.memory_manager.close()


async def main():
    """Application entry point"""
    from src.core.config import Settings
    
    settings = Settings()
    app = ClawdbotApp(settings)
    
    try:
        await app.start_server(
            host=settings.server_host,
            port=settings.server_port
        )
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())