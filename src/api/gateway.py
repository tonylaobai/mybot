"""
API endpoints for the Gateway component
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from src.core.config import Settings
from src.core.gateway import Gateway
from src.agents.manager import AgentManager
from src.channels.manager import ChannelManager
from src.memory.manager import MemoryManager
from src.tools.registry import ToolRegistry


router = APIRouter(prefix="/gateway", tags=["gateway"])


# Global references to system components
# In a real application, these would be dependency injected
_gateway: Gateway = None
_agent_manager: AgentManager = None
_channel_manager: ChannelManager = None
_memory_manager: MemoryManager = None
_tool_registry: ToolRegistry = None


def set_components(
    gateway: Gateway,
    agent_manager: AgentManager,
    channel_manager: ChannelManager,
    memory_manager: MemoryManager,
    tool_registry: ToolRegistry
):
    """Set the global component references"""
    global _gateway, _agent_manager, _channel_manager, _memory_manager, _tool_registry
    _gateway = gateway
    _agent_manager = agent_manager
    _channel_manager = channel_manager
    _memory_manager = memory_manager
    _tool_registry = tool_registry


@router.get("/health", summary="Get system health status")
async def get_health() -> Dict[str, Any]:
    """
    Get overall system health status including all components
    """
    if not _gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")
        
    health = await _gateway.health_check()
    return health


@router.get("/status", summary="Get detailed system status")
async def get_status() -> Dict[str, Any]:
    """
    Get detailed status of all system components
    """
    if not all([_gateway, _agent_manager, _channel_manager, _memory_manager]):
        raise HTTPException(status_code=503, detail="One or more components not initialized")
        
    status = {
        "timestamp": datetime.now().isoformat(),
        "gateway": await _gateway.health_check(),
        "agents": await _agent_manager.health_check(),
        "channels": await _channel_manager.health_check(),
        "memory": await _memory_manager.health_check(),
        "tools_registered": len(_tool_registry.list_tools()) if _tool_registry else 0
    }
    
    return status


@router.post("/message/route", summary="Route a message between components")
async def route_message(
    source: str,
    destination: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Route a message from source to destination through the gateway
    """
    if not _gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")
        
    try:
        result = await _gateway.route_message(source, destination, message_data)
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error routing message: {str(e)}")


@router.get("/agents/list", summary="List all available agents")
async def list_agents() -> List[str]:
    """
    Get a list of all available agent IDs
    """
    if not _agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
    return await _agent_manager.list_agents()


@router.post("/agents/{agent_id}/message", summary="Send message to specific agent")
async def send_to_agent(agent_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message to a specific agent
    """
    if not _agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
    agent = await _agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
    try:
        result = await agent.process_message(message_data)
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/channels/list", summary="List all available channels")
async def list_channels() -> List[str]:
    """
    Get a list of all available channel IDs
    """
    if not _channel_manager:
        raise HTTPException(status_code=503, detail="Channel manager not initialized")
        
    return await _channel_manager.list_channels()


@router.post("/channels/{channel_id}/send", summary="Send message via specific channel")
async def send_via_channel(channel_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message via a specific channel
    """
    if not _channel_manager:
        raise HTTPException(status_code=503, detail="Channel manager not initialized")
        
    channel = await _channel_manager.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
        
    try:
        result = await _channel_manager.send_message(channel_id, message_data)
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")


@router.get("/memory/search", summary="Search memory entries")
async def search_memory(query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search memory entries based on query
    """
    if not _memory_manager:
        raise HTTPException(status_code=503, detail="Memory manager not initialized")
        
    try:
        results = await _memory_manager.search_memory(query, category, limit)
        return [
            {
                "id": entry.id,
                "timestamp": entry.timestamp.isoformat(),
                "category": entry.category,
                "content": entry.content,
                "tags": entry.tags,
                "importance": entry.importance
            }
            for entry in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memory: {str(e)}")


@router.post("/memory/store", summary="Store a memory entry")
async def store_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store a new memory entry
    """
    if not _memory_manager:
        raise HTTPException(status_code=503, detail="Memory manager not initialized")
        
    try:
        await _memory_manager.store_memory(memory_data)
        return {
            "success": True,
            "id": memory_data.get('id', f"mem_{datetime.now().timestamp()}"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")


@router.get("/tools/list", summary="List all available tools")
async def list_tools() -> List[str]:
    """
    Get a list of all available tool names
    """
    if not _tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
        
    return _tool_registry.list_tools()


@router.post("/tools/{tool_name}/execute", summary="Execute a specific tool")
async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a specific tool with given arguments
    """
    if not _tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
        
    if tool_name not in _tool_registry.list_tools():
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
    try:
        result = await _tool_registry.execute_tool(tool_name, **tool_args)
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")


@router.get("/tools/{tool_name}/schema", summary="Get tool schema")
async def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """
    Get the schema for a specific tool
    """
    if not _tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
        
    schema = _tool_registry.get_tool_schema(tool_name)
    if not schema:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
    return schema


@router.get("/interactions/recent", summary="Get recent interactions")
async def get_recent_interactions(user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent interactions, optionally filtered by user
    """
    if not _memory_manager:
        raise HTTPException(status_code=503, detail="Memory manager not initialized")
        
    try:
        interactions = await _memory_manager.get_recent_interactions(user_id, limit)
        return [
            {
                "id": interaction.id,
                "timestamp": interaction.timestamp.isoformat(),
                "source": interaction.source,
                "user_id": interaction.user_id,
                "input_text": interaction.input_text,
                "output_text": interaction.output_text,
                "session_id": interaction.session_id
            }
            for interaction in interactions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interactions: {str(e)}")


@router.post("/system/notification", summary="Send system notification")
async def send_system_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a system notification through the gateway
    """
    if not _gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")
        
    try:
        result = await _gateway.route_message(
            "system", 
            "internal", 
            {
                "type": "system_notification",
                **notification_data
            }
        )
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending notification: {str(e)}")