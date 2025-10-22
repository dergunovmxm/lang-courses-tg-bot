from datetime import datetime
from typing import Optional, Dict, Any

class User:
    def __init__(self, 
                 telegram_id: int,
                 username: str,
                 first_name: str,
                 last_name: Optional[str] = None,
                 language_code: str = 'ru',
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 is_active: bool = True):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language_code = language_code
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.is_active = is_active
    
    def to_dict(self) -> Dict[str, Any]:
        
        #Конвертация в словарь для Supabase

        return {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language_code': self.language_code,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        
        #Создание объекта User из словаря Supabase

        return cls(
            telegram_id=data['telegram_id'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            language_code=data.get('language_code', 'ru'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_active=data.get('is_active', True)
        )

class UserSettings:
    def __init__(self,
                 telegram_id: int,
                 notification_enabled: bool = True,
                 daily_reminder_time: str = "09:00",
                 language_level: str = "beginner",
                 target_language: str = "en"):
        self.telegram_id = telegram_id
        self.notification_enabled = notification_enabled
        self.daily_reminder_time = daily_reminder_time
        self.language_level = language_level
        self.target_language = target_language
    
    def to_dict(self) -> Dict[str, Any]:
        
        #Конвертация в словарь для Supabase

        return {
            'telegram_id': self.telegram_id,
            'notification_enabled': self.notification_enabled,
            'daily_reminder_time': self.daily_reminder_time,
            'language_level': self.language_level,
            'target_language': self.target_language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        
        #Создание объекта UserSettings из словаря Supabase
        
        return cls(
            telegram_id=data['telegram_id'],
            notification_enabled=data.get('notification_enabled', True),
            daily_reminder_time=data.get('daily_reminder_time', "09:00"),
            language_level=data.get('language_level', 'beginner'),
            target_language=data.get('target_language', 'en')
        )
