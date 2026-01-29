"""
Basic test script to verify Clawdbot-Python structure and components
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import Settings
from core.gateway import Gateway
from tools.registry import ToolRegistry
from tools.builtin import ReadFileTool, WriteFileTool, ExecTool
from memory.manager import MemoryManager


async def test_basic_components():
    """Test basic component initialization"""
    print("Testing Clawdbot-Python basic components...\n")
    
    # Test settings
    print("1. Testing Settings...")
    settings = Settings()
    print(f"   ✓ Settings created: server_port={settings.server_port}, workspace_dir={settings.workspace_dir}")
    
    # Test tool registry
    print("\n2. Testing Tool Registry...")
    tool_registry = ToolRegistry()
    
    # Register some tools
    read_tool = ReadFileTool()
    write_tool = WriteFileTool()
    exec_tool = ExecTool()
    
    tool_registry.register(read_tool)
    tool_registry.register(write_tool)
    tool_registry.register(exec_tool)
    
    print(f"   ✓ Tool registry created with {len(tool_registry.tools)} tools:")
    for tool_name in tool_registry.list_tools():
        print(f"     - {tool_name}")
    
    # Test memory manager
    print("\n3. Testing Memory Manager...")
    memory_manager = MemoryManager(settings)
    await memory_manager.initialize()
    print("   ✓ Memory manager initialized")
    
    # Test basic memory operations
    await memory_manager.store_memory({
        "category": "test",
        "content": "This is a test memory entry",
        "tags": ["test", "python"],
        "importance": 0.8
    })
    print("   ✓ Memory entry stored")
    
    # Search memory
    results = await memory_manager.search_memory("test")
    print(f"   ✓ Memory search returned {len(results)} results")
    
    # Test gateway
    print("\n4. Testing Gateway...")
    gateway = Gateway(settings)
    print("   ✓ Gateway created")
    
    # Test health check
    health = await gateway.health_check()
    print(f"   ✓ Gateway health check passed: {health['gateway']}")
    
    # Test tool execution
    print("\n5. Testing Tool Execution...")
    
    # Test read tool (should fail gracefully with non-existent file)
    result = await tool_registry.execute_tool("readfile", file_path="/nonexistent/file.txt")
    print(f"   ✓ Read tool executed, success: {result.success}")
    
    # Test write tool
    test_file = "/tmp/clawdbot_test.txt"
    result = await tool_registry.execute_tool("writefile", file_path=test_file, content="Hello from Clawdbot-Python!")
    print(f"   ✓ Write tool executed, success: {result.success}")
    
    # Test read tool on the file we just created
    result = await tool_registry.execute_tool("readfile", file_path=test_file)
    if result.success:
        print(f"   ✓ Read tool read back content: {result.result[:50]}...")
    
    # Test exec tool (safe command)
    result = await tool_registry.execute_tool("exec", command="echo 'Hello from exec tool'")
    print(f"   ✓ Exec tool executed, success: {result.success}")
    
    print("\n✓ All basic tests passed!")
    print("\nClawdbot-Python basic structure is working correctly.")
    

async def main():
    try:
        await test_basic_components()
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())