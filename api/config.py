"""
Configuration management for Campus Climb application.
Handles environment variables and default settings.
"""
import os

class Config:
    """Application configuration"""
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')
    OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '60'))
    
    # AI Assistant Settings
    AI_ASSISTANT_ENABLED = os.environ.get('AI_ASSISTANT_ENABLED', 'true').lower() == 'true'
    AI_RATE_LIMIT_PER_HOUR = int(os.environ.get('AI_RATE_LIMIT_PER_HOUR', '10'))
    
    @staticmethod
    def get_ollama_url():
        """Get the full Ollama API URL"""
        base = Config.OLLAMA_BASE_URL.rstrip('/')
        return f"{base}/api/generate"
    
    @staticmethod
    def is_ai_enabled():
        """Check if AI assistant is enabled"""
        return Config.AI_ASSISTANT_ENABLED

