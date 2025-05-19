import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-very-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://admin:ppp2025@localhost/sistemallamadas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pushover configuration
    PUSHOVER_API_TOKEN = os.environ.get('PUSHOVER_API_TOKEN') or 'your_api_token'
    PUSHOVER_USER_KEY = os.environ.get('PUSHOVER_USER_KEY') or 'your_user_key'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@sistemallamadas.com' 