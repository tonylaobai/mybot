"""
Configuration management for Clawdbot-Python
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=8000, description="Server port")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Workspace
    workspace_dir: Path = Field(default=Path("~/clawd").expanduser(), description="Workspace directory")
    
    # Memory
    memory_dir: Path = Field(default=Path("~/clawd/memory").expanduser(), description="Memory directory")
    memory_retention_days: int = Field(default=30, description="Memory retention in days")
    
    # Models
    default_model: str = Field(default="gpt-4o", description="Default AI model")
    fallback_models: List[str] = Field(default=["gpt-4-turbo", "claude-3-opus"], description="Fallback models")
    
    # Channels
    enabled_channels: List[str] = Field(default=["whatsapp", "telegram", "discord"], description="Enabled channels")
    
    # Security
    enable_sandbox: bool = Field(default=True, description="Enable execution sandbox")
    allowed_exec_commands: List[str] = Field(default=["ls", "cat", "echo"], description="Allowed commands in sandbox")
    
    # Tools
    enabled_tools: List[str] = Field(default=["read", "write", "web_search"], description="Enabled tools")
    
    # API Keys (can be set via environment variables)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API Key")
    google_api_key: Optional[str] = Field(default=None, description="Google API Key")
    
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./clawdbot.db", description="Database URL")
    
    # Redis (for caching and pub/sub)
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    
    # Session settings
    session_timeout_minutes: int = Field(default=1440, description="Session timeout in minutes (24 hours)")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Requests per minute per IP")
    rate_limit_window_seconds: int = Field(default=60, description="Rate limit window in seconds")
    
    class Config:
        env_file = ".env"
        env_prefix = "CLAWDBOT_"


class ChannelConfig:
    """Configuration for individual channels"""
    
    def __init__(self, channel_type: str, config_dict: dict):
        self.channel_type = channel_type
        self.config = config_dict
        
    @property
    def enabled(self) -> bool:
        return self.config.get('enabled', True)
        
    @property
    def credentials(self) -> dict:
        return self.config.get('credentials', {})
        
    @property
    def webhook_url(self) -> Optional[str]:
        return self.config.get('webhook_url')
        
    @property
    def message_handling(self) -> dict:
        return self.config.get('message_handling', {})


class ToolConfig:
    """Configuration for tools"""
    
    def __init__(self, tool_name: str, config_dict: dict):
        self.tool_name = tool_name
        self.config = config_dict
        
    @property
    def enabled(self) -> bool:
        return self.config.get('enabled', True)
        
    @property
    def permissions(self) -> dict:
        return self.config.get('permissions', {})
        
    @property
    def settings(self) -> dict:
        return self.config.get('settings', {})