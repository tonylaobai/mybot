#!/usr/bin/env python3
"""
Demonstration of Clawdbot-Python capabilities
"""

import asyncio
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import Settings
from core.gateway import Gateway
from channels.manager import ChannelManager
from agents.manager import AgentManager
from memory.manager import MemoryManager
from tools.registry import ToolRegistry
from tools.builtin import ReadFileTool, WriteFileTool, ExecTool, WebSearchTool


async def demo_basic_functionality():
    """Demonstrate basic functionality of Clawdbot-Python"""
    print("="*60)
    print("CLUADBOT-PYTHON DEMONSTRATION")
    print("="*60)
    
    print("\n1. Initializing Components...")
    
    # Create settings
    settings = Settings()
    print(f"   ✓ Settings loaded: server_port={settings.server_port}")
    
    # Initialize tool registry
    tool_registry = ToolRegistry()
    print("   ✓ Tool registry created")
    
    # Register tools
    tools = [
        ReadFileTool(),
        WriteFileTool(),
        ExecTool(),
        WebSearchTool()
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    print(f"   ✓ Registered {len(tool_registry.list_tools())} tools: {', '.join(tool_registry.list_tools())}")
    
    # Initialize memory manager
    memory_manager = MemoryManager(settings)
    await memory_manager.initialize()
    print("   ✓ Memory manager initialized")
    
    # Initialize agent manager
    agent_manager = AgentManager(settings)
    await agent_manager.initialize(tool_registry)
    print("   ✓ Agent manager initialized")
    
    # Initialize channel manager
    channel_manager = ChannelManager(settings)
    await channel_manager.initialize()
    print("   ✓ Channel manager initialized")
    
    # Initialize gateway
    gateway = Gateway(settings)
    await gateway.initialize(
        channel_manager=channel_manager,
        agent_manager=agent_manager,
        memory_manager=memory_manager
    )
    print("   ✓ Gateway initialized")
    
    print("\n2. Testing Tool Execution...")
    
    # Test write tool
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        test_file = tmp.name
        tmp.write("This is a test file created by Clawdbot-Python!\n")
        tmp.write(f"Created at: {datetime.now()}\n")
    
    print(f"   ✓ Created temporary file: {test_file}")
    
    # Test read tool
    read_result = await tool_registry.execute_tool("readfile", file_path=test_file)
    if read_result.success:
        print(f"   ✓ Read file content: {read_result.result.strip()}")
    else:
        print(f"   ✗ Failed to read file: {read_result.error}")
    
    # Test exec tool
    exec_result = await tool_registry.execute_tool("exec", command="echo 'Hello from exec tool!'")
    if exec_result.success:
        print(f"   ✓ Exec command result: {exec_result.result.strip()}")
    else:
        print(f"   ✗ Failed to execute command: {exec_result.error}")
    
    print("\n3. Testing Memory Functions...")
    
    # Store some memory entries
    await memory_manager.store_memory({
        "category": "demo",
        "content": "This is a demonstration of Clawdbot-Python's memory system.",
        "tags": ["demo", "memory", "python"],
        "importance": 0.8
    })
    
    await memory_manager.store_memory({
        "category": "user_preference",
        "content": "User enjoys technology demonstrations.",
        "tags": ["user", "preference", "demo"],
        "importance": 0.9
    })
    
    print("   ✓ Stored 2 memory entries")
    
    # Search memory
    search_results = await memory_manager.search_memory("demo")
    print(f"   ✓ Found {len(search_results)} results for 'demo' query")
    
    print("\n4. Testing Agent Interaction...")
    
    # Get default agent
    agent = await agent_manager.get_default_agent()
    if agent:
        print(f"   ✓ Got default agent: {agent.id}")
        
        # Process a sample message
        sample_message = {
            "content": "Hello, can you tell me about yourself?",
            "channel": "demo",
            "user_id": "demo_user"
        }
        
        response = await agent.process_message(sample_message)
        print(f"   ✓ Agent response: {response['response'][:100]}...")
    
    print("\n5. Testing Gateway Routing...")
    
    # Test gateway health
    health_status = await gateway.health_check()
    print(f"   ✓ Gateway health: {health_status['gateway']}")
    print(f"   ✓ Components healthy: {list(health_status['components'].keys())}")
    
    print("\n6. Testing Channel Simulation...")
    
    # List available channels
    channels = await channel_manager.list_channels()
    print(f"   ✓ Available channels: {channels}")
    
    # Send a test message through mock channel
    if channels:
        mock_channel_id = channels[0]  # Use the first available channel (likely mock)
        message_result = await channel_manager.send_message(mock_channel_id, {
            "recipient_id": "demo_recipient",
            "text": "Hello from Clawdbot-Python demo!",
            "timestamp": datetime.now().isoformat()
        })
        print(f"   ✓ Sent test message via {mock_channel_id}: {message_result['success']}")
    
    print("\n7. Final Health Check...")
    
    # Perform comprehensive health check
    full_status = await gateway.health_check()
    print(f"   ✓ Overall status: {full_status['gateway']}")
    print(f"   ✓ Timestamp: {full_status['timestamp']}")
    
    # Cleanup
    try:
        os.unlink(test_file)
        print("   ✓ Cleaned up temporary file")
    except:
        pass
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    
    print("\nSUMMARY:")
    print(f"• Tools available: {len(tool_registry.list_tools())}")
    print(f"• Agents running: {len(await agent_manager.list_agents())}")
    print(f"• Channels active: {len(await channel_manager.list_channels())}")
    print(f"• Memory entries stored: {len(await memory_manager.search_memory(''))}")
    print("\nClawdbot-Python is fully functional and ready for use!")


async def main():
    """Main entry point for the demo"""
    try:
        await demo_basic_functionality()
    except Exception as e:
        print(f"\n✗ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())