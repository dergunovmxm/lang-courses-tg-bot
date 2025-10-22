from .supabase_client import supabase_client
from .models import User, UserSettings
from typing import Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserCRUD:
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        
        #Получить пользователя по Telegram ID

        try:
            result = supabase_client.select(
                'users', 
                filters={'telegram_id': telegram_id},
                limit=1
            )
            if result:
                return User.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {telegram_id}: {e}")
            return None
    
    def create_user(self, telegram_id: int, username: str, 
                   first_name: str, last_name: str = None, 
                   language_code: str = 'ru') -> Optional[User]:
       
        #Создать нового пользователя

        try:
            user_data = {
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            result = supabase_client.insert('users', user_data)
            if result:
                logger.info(f"Создан новый пользователь: {telegram_id}")
                return User.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка создания пользователя {telegram_id}: {e}")
            return None
    
    def get_or_create_user(self, telegram_id: int, username: str, 
                          first_name: str, last_name: str = None, 
                          language_code: str = 'ru') -> Optional[User]:
        
        #Получить или создать пользователя

        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            # Обновляем данные существующего пользователя
            try:
                update_data = {
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'language_code': language_code,
                    'updated_at': datetime.now().isoformat()
                }
                
                result = supabase_client.update(
                    'users', 
                    {'telegram_id': telegram_id}, 
                    update_data
                )
                if result:
                    return User.from_dict(result)
                else:
                    return user  # Возвращаем старые данные если обновление не удалось
            except Exception as e:
                logger.error(f"Ошибка обновления пользователя {telegram_id}: {e}")
                return user
        else:
            return self.create_user(telegram_id, username, first_name, last_name, language_code)

class UserSettingsCRUD:
    def get_user_settings(self, telegram_id: int) -> Optional[UserSettings]:
        
        #Получить настройки пользователя

        try:
            result = supabase_client.select(
                'user_settings', 
                filters={'telegram_id': telegram_id},
                limit=1
            )
            if result:
                return UserSettings.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Ошибка получения настроек пользователя {telegram_id}: {e}")
            return None
    
    def create_default_settings(self, telegram_id: int) -> Optional[UserSettings]:
        
        #Создать настройки по умолчанию для пользователя

        try:
            settings_data = {
                'telegram_id': telegram_id,
                'notification_enabled': True,
                'daily_reminder_time': "09:00",
                'language_level': "beginner",
                'target_language': "en",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = supabase_client.insert('user_settings', settings_data)
            if result:
                return UserSettings.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка создания настроек пользователя {telegram_id}: {e}")
            return None
    
    def update_notification_settings(self, telegram_id: int, enabled: bool) -> Optional[UserSettings]:
        
        #Обновить настройки уведомлений
        
        try:
            settings = self.get_user_settings(telegram_id)
            if not settings:
                settings = self.create_default_settings(telegram_id)
                if not settings:
                    return None
            
            update_data = {
                'notification_enabled': enabled,
                'updated_at': datetime.now().isoformat()
            }
            
            result = supabase_client.update(
                'user_settings', 
                {'telegram_id': telegram_id}, 
                update_data
            )
            if result:
                return UserSettings.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления настроек уведомлений {telegram_id}: {e}")
            return None

# Создаем глобальные экземпляры CRUD классов
user_crud = UserCRUD()
settings_crud = UserSettingsCRUD()