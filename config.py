import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Firebase configuration
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    
    # OpenAI API configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'gpt-4o')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # Interview settings
    DEFAULT_INTERVIEW_DURATION = 30  # minutes
    MAX_QUESTIONS = 15
    DEFAULT_PERSONA = 'technical_expert'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Set the active configuration based on the FLASK_ENV environment variable
active_config = config_by_name.get(os.environ.get('FLASK_ENV', 'development'), DevelopmentConfig)