"""Configuration settings for the AI Knowledge Base application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Settings
    openai_api_key: str = ""
    
    # Anthropic Settings (optional)
    anthropic_api_key: Optional[str] = None
    
    # Confluence Settings
    confluence_url: Optional[str] = None
    confluence_username: Optional[str] = None
    confluence_api_token: Optional[str] = None
    
    # Slack Settings
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None
    
    # Vector Database
    chroma_persist_directory: str = "./data/chroma"
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Model Settings
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
