"""
Tool Registry for Clawdbot-Python
Manages registration, discovery, and execution of tools
"""

import inspect
from typing import Dict, List, Any, Callable, Type, Optional, Union
from pydantic import BaseModel
import asyncio
import logging


class ToolParameter(BaseModel):
    """Represents a parameter for a tool"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolResult(BaseModel):
    """Represents the result of a tool execution"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool:
    """Base class for all tools"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '')
        self.description = getattr(self, '__doc__', 'No description provided')
        self.parameters = self._get_parameters()
        self.logger = logging.getLogger(f"tools.{self.name}")
        
    def _get_parameters(self) -> List[ToolParameter]:
        """Extract parameters from the tool's run method"""
        sig = inspect.signature(self.run)
        params = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_info = ToolParameter(
                name=param_name,
                type=str(param.annotation) if param.annotation != inspect.Parameter.empty else 'string',
                description=f'Description for {param_name}',
                required=param.default == inspect.Parameter.empty,
                default=param.default if param.default != inspect.Parameter.empty else None
            )
            params.append(param_info)
            
        return params
        
    async def run(self, **kwargs) -> Any:
        """Execute the tool with the given parameters"""
        raise NotImplementedError("Tool must implement run method")
        
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema for AI model consumption"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type.lower() if isinstance(param.type, str) else str(param.type),
                        "description": param.description
                    } for param in self.parameters
                },
                "required": [param.name for param in self.parameters if param.required]
            }
        }


class ToolRegistry:
    """Registry for managing tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logging.getLogger("tools.registry")
        
    def register(self, tool: BaseTool):
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
        
    def unregister(self, tool_name: str):
        """Unregister a tool from the registry"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(f"Unregistered tool: {tool_name}")
            
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
        
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
        
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a specific tool"""
        tool = self.get_tool(tool_name)
        return tool.get_schema() if tool else None
        
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools"""
        return [tool.get_schema() for tool in self.tools.values()]
        
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool with the given parameters"""
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not found"
                )
                
            result = await tool.run(**kwargs)
            return ToolResult(success=True, result=result)
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return ToolResult(
                success=False,
                error=str(e)
            )
            
    def validate_parameters(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for a tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        validated_params = {}
        for param_def in tool.parameters:
            if param_def.name in params:
                validated_params[param_def.name] = params[param_def.name]
            elif param_def.required and param_def.default is None:
                raise ValueError(f"Required parameter '{param_def.name}' is missing")
            elif param_def.default is not None:
                validated_params[param_def.name] = param_def.default
                
        return validated_params