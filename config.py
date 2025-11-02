import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

class Config:
    BASE_DIR = Path(__file__).parent
    load_dotenv(BASE_DIR / ".env")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    @classmethod
    def validate(cls):
        
        #Проверка наличия обязательных переменных окружения
        
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL не найден в переменных окружения")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY не найден в переменных окружения")

config = Config()