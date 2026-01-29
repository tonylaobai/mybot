"""
Built-in tools for Clawdbot-Python
"""

import asyncio
import subprocess
import aiofiles
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from src.tools.registry import BaseTool


class ReadFileTool(BaseTool):
    """Read the contents of a file"""
    
    async def run(self, file_path: str) -> str:
        """
        Read the contents of a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Contents of the file as a string
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except FileNotFoundError:
            return f"Error: File not found: {file_path}"
        except PermissionError:
            return f"Error: Permission denied to read file: {file_path}"
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"


class WriteFileTool(BaseTool):
    """Write content to a file"""
    
    async def run(self, file_path: str, content: str) -> str:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            
        Returns:
            Success or error message
        """
        try:
            # Create parent directories if they don't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except PermissionError:
            return f"Error: Permission denied to write file: {file_path}"
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"


class ExecTool(BaseTool):
    """Execute shell commands"""
    
    async def run(self, command: str, timeout: int = 30) -> str:
        """
        Execute a shell command.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (default 30)
            
        Returns:
            Command output or error message
        """
        try:
            # Validate command to prevent dangerous operations
            dangerous_patterns = ['rm -rf', '>', '/dev/', 'mv ', 'dd ']
            cmd_lower = command.lower()
            for pattern in dangerous_patterns:
                if pattern in cmd_lower:
                    return f"Error: Dangerous command pattern detected: {pattern}"
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                result = ""
                if stdout:
                    result += f"STDOUT:\n{stdout.decode()}"
                if stderr:
                    result += f"\nSTDERR:\n{stderr.decode()}"
                    
                if process.returncode != 0:
                    result += f"\nReturn code: {process.returncode}"
                    
                return result.strip()
                
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Command timed out after {timeout} seconds"
                
        except Exception as e:
            return f"Error executing command '{command}': {str(e)}"


class WebSearchTool(BaseTool):
    """Perform web searches (using a search API)"""
    
    async def run(self, query: str, num_results: int = 5) -> str:
        """
        Perform a web search.
        
        Args:
            query: Search query
            num_results: Number of results to return (default 5)
            
        Returns:
            Search results as JSON string
        """
        # Note: This is a placeholder implementation
        # In a real system, you'd integrate with a search API like Brave, SerpAPI, etc.
        try:
            # For demonstration purposes, we'll return a mock response
            # In production, replace with actual search API integration
            mock_results = {
                "query": query,
                "num_results": num_results,
                "results": [
                    {
                        "title": f"Mock result for {query}",
                        "url": "https://example.com",
                        "snippet": f"This is a mock search result for the query: {query}"
                    }
                    for i in range(num_results)
                ]
            }
            return json.dumps(mock_results, indent=2)
        except Exception as e:
            return f"Error performing web search: {str(e)}"


class BrowserTool(BaseTool):
    """Simulate browser operations (in a real implementation, this would use Playwright or Selenium)"""
    
    async def run(self, url: str, operation: str = "get_content") -> str:
        """
        Simulate browser operations.
        
        Args:
            url: URL to operate on
            operation: Operation to perform (get_content, screenshot, etc.)
            
        Returns:
            Result of the operation
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return f"Error: Invalid URL format: {url}"
                
            if operation == "get_content":
                # For demonstration, just return a mock response
                # In production, use Playwright or similar
                response = {
                    "url": url,
                    "title": f"Mock page for {parsed.netloc}",
                    "content_preview": f"This is a mock preview of the content at {url}",
                    "status_code": 200
                }
                return json.dumps(response, indent=2)
            else:
                return f"Operation '{operation}' not implemented in mock browser tool"
                
        except Exception as e:
            return f"Error with browser operation: {str(e)}"


class MessageTool(BaseTool):
    """Send messages through various channels"""
    
    async def run(self, channel: str, recipient: str, message: str) -> str:
        """
        Send a message through a specified channel.
        
        Args:
            channel: Channel to send message through (whatsapp, telegram, etc.)
            recipient: Recipient identifier
            message: Message content
            
        Returns:
            Result of the send operation
        """
        # This would integrate with the channel manager in a real implementation
        result = {
            "channel": channel,
            "recipient": recipient,
            "message_sent": len(message),
            "status": "mock_sent",  # Would be actual status in real implementation
            "timestamp": "2024-01-29T04:30:00Z"
        }
        return json.dumps(result, indent=2)


class GatewayTool(BaseTool):
    """Gateway management operations"""
    
    async def run(self, operation: str, **kwargs) -> str:
        """
        Perform gateway management operations.
        
        Args:
            operation: Operation to perform (status, restart, config, etc.)
            **kwargs: Additional parameters for the operation
            
        Returns:
            Result of the operation
        """
        try:
            if operation == "status":
                # Return mock gateway status
                status = {
                    "status": "running",
                    "uptime": "1 hour",
                    "connected_channels": ["whatsapp", "telegram"],
                    "active_agents": 1,
                    "memory_usage": "128 MB",
                    "timestamp": "2024-01-29T04:30:00Z"
                }
                return json.dumps(status, indent=2)
            elif operation == "config_get":
                # Return mock config
                config = {
                    "server_host": "0.0.0.0",
                    "server_port": 8000,
                    "log_level": "INFO",
                    "workspace_dir": "~/clawd",
                    "enabled_channels": ["whatsapp", "telegram", "discord"]
                }
                return json.dumps(config, indent=2)
            else:
                return f"Operation '{operation}' not implemented in mock gateway tool"
                
        except Exception as e:
            return f"Error with gateway operation: {str(e)}"


class SessionsTool(BaseTool):
    """Session management operations"""
    
    async def run(self, operation: str, **kwargs) -> str:
        """
        Perform session management operations.
        
        Args:
            operation: Operation to perform (list, create, delete, etc.)
            **kwargs: Additional parameters for the operation
            
        Returns:
            Result of the operation
        """
        try:
            if operation == "list":
                # Return mock session list
                sessions = [
                    {
                        "session_id": "session_001",
                        "user_id": "user_123",
                        "channel": "whatsapp",
                        "created_at": "2024-01-29T04:00:00Z",
                        "last_activity": "2024-01-29T04:30:00Z",
                        "active": True
                    },
                    {
                        "session_id": "session_002", 
                        "user_id": "user_456",
                        "channel": "telegram",
                        "created_at": "2024-01-29T03:45:00Z",
                        "last_activity": "2024-01-29T04:15:00Z",
                        "active": False
                    }
                ]
                return json.dumps(sessions, indent=2)
            elif operation == "status":
                status = {
                    "total_sessions": 2,
                    "active_sessions": 1,
                    "recent_messages": 15,
                    "timestamp": "2024-01-29T04:30:00Z"
                }
                return json.dumps(status, indent=2)
            else:
                return f"Operation '{operation}' not implemented in mock sessions tool"
                
        except Exception as e:
            return f"Error with sessions operation: {str(e)}"