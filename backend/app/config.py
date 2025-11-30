"""
Configuration management for the Flask application
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # LLM Parameters
    LLM_TEMPERATURE = float(os.environ.get('LLM_TEMPERATURE', '0.7'))
    LLM_MAX_TOKENS = int(os.environ.get('LLM_MAX_TOKENS', '100'))  # Reduced for faster, concise responses

    # Mistral Cloud settings (accept legacy misspelling 'Mirstal')
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY') or os.environ.get('Mirstal')
    MISTRAL_API_BASE = os.environ.get('MISTRAL_API_BASE', 'https://api.mistral.ai')
    MISTRAL_MODEL = os.environ.get('MISTRAL_MODEL', 'mistral-large-latest')
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_ENABLED = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///voicebot.db')
    
    # Session Configuration
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 hour
    
    # Rate Limiting
    # Priority weighting for input modes (0.0‑1.0). Higher value means higher priority.
    VOICE_PRIORITY = float(os.environ.get('VOICE_PRIORITY', '0.6'))
    TEXT_PRIORITY = float(os.environ.get('TEXT_PRIORITY', '0.4'))
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '30'))
    RATE_LIMIT_PER_HOUR = int(os.environ.get('RATE_LIMIT_PER_HOUR', '100'))
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm', 'ogg', 'm4a'}
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Cache Configuration
    CACHE_TTL = int(os.environ.get('CACHE_TTL', '3600'))  # 1 hour
    
    # Performance
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///test_voicebot.db'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

