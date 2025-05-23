import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-very-secret'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:ppp2025@localhost/sistemallamadas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Pushover
    PUSHOVER_API_TOKEN = 'a5rzbhbgyms8aggkz4m99wddfepugf'
    PUSHOVER_USER_KEY = 'uhnir2p968ypnrgzf9ncupvhiet9pj'
    
    # Configuración de correo electrónico
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'bryanramoscruz@gmail.com'
    MAIL_PASSWORD = 'cqqx zdpp drld shfm'
    MAIL_DEFAULT_SENDER = 'bryanramoscruz@gmail.com'
    
    # Configuración de sistema de relés
    SERVER_IP = '172.17.0.10'  # IP del servidor para recibir llamadas
    RELAY_BASE_IP = '172.17.2'  # Base de IP para los relés (formato: 172.17.2.xxx)
    RELAY_ENDPOINT = '/relay/0'  # Endpoint para controlar los relés
    
    # Modo de simulación (True = usar imágenes locales, False = conectar a relés físicos)
    SIMULATION_MODE = True 