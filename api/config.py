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
    
    # AI Filter Settings
    AI_FILTER_ENABLED = os.environ.get('AI_FILTER_ENABLED', 'true').lower() == 'true'
    AI_FILTER_MODEL = os.environ.get('AI_FILTER_MODEL', None)  # None = use OLLAMA_MODEL
    AI_FILTER_TIMEOUT = int(os.environ.get('AI_FILTER_TIMEOUT', '120'))  # 120s default (llama loads slowly on first run)
    AI_FILTER_FALLBACK = os.environ.get('AI_FILTER_FALLBACK', 'true').lower() == 'true'
    AI_FILTER_MIN_CONFIDENCE = float(os.environ.get('AI_FILTER_MIN_CONFIDENCE', '0.7'))  # Reject AI "true" if confidence below this
    # When True, reject opportunities when Ollama is unavailable (no keyword fallback) - avoids false positives
    AI_FILTER_REJECT_ON_ERROR = os.environ.get('AI_FILTER_REJECT_ON_ERROR', 'true').lower() == 'true'
    # Comma-separated source names that skip AI filter (e.g. "jooble,authentic_jobs" - API job boards are usually clean)
    SOURCES_SKIP_AI_FILTER_STR = os.environ.get('SOURCES_SKIP_AI_FILTER', '')
    SOURCES_SKIP_AI_FILTER = [s.strip().lower() for s in SOURCES_SKIP_AI_FILTER_STR.split(',') if s.strip()]
    
    @staticmethod
    def get_ollama_url():
        """Get the full Ollama API URL"""
        base = Config.OLLAMA_BASE_URL.rstrip('/')
        return f"{base}/api/generate"
    
    @staticmethod
    def is_ai_enabled():
        """Check if AI assistant is enabled"""
        return Config.AI_ASSISTANT_ENABLED
    
    @staticmethod
    def is_ai_filter_enabled():
        """Check if AI filtering is enabled"""
        return Config.AI_FILTER_ENABLED

