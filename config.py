import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')  # Default to GPT-4 if not specified

# Firebase configuration
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')

# Web scraper configuration
SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY')

# Application configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# RAG configuration
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', 'vector_db')

# Interview configuration
MAX_QUESTIONS = int(os.getenv('MAX_QUESTIONS', '10'))
INTERVIEW_DURATION = int(os.getenv('INTERVIEW_DURATION', '30'))  # in minutes