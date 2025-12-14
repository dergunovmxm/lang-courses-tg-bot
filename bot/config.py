import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    # load_dotenv(BASE_DIR / ".env")
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST')
    POSTGRESQL_PORT = os.getenv('POSTGRESQL_PORT')
    POSTGRESQL_USER = os.getenv('POSTGRESQL_USER')
    POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
    POSTGRESQL_DBNAME = os.getenv('POSTGRESQL_DBNAME')
    API_DEEPSEEK = os.getenv('API_DEEPSEEK')
    @classmethod
    def validate(cls):
        
        #Проверка наличия обязательных переменных окружения
        
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
        if not cls.POSTGRESQL_HOST:
            raise ValueError("POSTGRESQL_HOST не найден в переменных окружения")
        if not cls.POSTGRESQL_PORT:
            raise ValueError("POSTGRESQL_PORT не найден в переменных окружения")
        if not cls.POSTGRESQL_USER:
            raise ValueError("POSTGRESQL_USER не найден в переменных окружения")
        if not cls.POSTGRESQL_PASSWORD:
            raise ValueError("POSTGRESQL_PASSWORD не найден в переменных окружения")
        if not cls.POSTGRESQL_DBNAME:
            raise ValueError("POSTGRESQL_DBNAME не найден в переменных окружения")
        if not cls.API_DEEPSEEK:
            raise ValueError('API_DEEPSEEK не найден в переменных окружения')
config = Config()