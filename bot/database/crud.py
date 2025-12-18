from .connection import postgresql_client
from typing import Optional, Dict, Any
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from .connection import postgresql_client
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserCRUD:
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя по telegram_id"""
        try:
            # Используем метод select из PostgreSQLClient с фильтрацией
            users = postgresql_client.select('users', limit=100)  # Получаем больше записей для фильтрации
            
            # Фильтруем в памяти (можно оптимизировать через WHERE в запросе)
            for user in users:
                if user.get('telegram_id') == telegram_id:
                    logger.info(f"👤 Пользователь {telegram_id} найден в базе")
                    return user
            
            logger.info(f"👤 Пользователь {telegram_id} не найден в базе")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {telegram_id}: {e}")
            return None
    
    def create_user(self, telegram_id: int, username: str, first_name: str,
                last_name: str = None, language_code: str = 'ru', 
                chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        try:
            now = datetime.utcnow().isoformat()
            user_data = {
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'chat_id': chat_id,
                'updated_at': now,
                'is_active': True
            }
            # Убираем None
            user_data = {k: v for k, v in user_data.items() if v is not None}

            # Передаём created_at отдельно — только для INSERT
            result = postgresql_client.upsert('users', user_data, 'telegram_id')
            
            if result:
                logger.info(f"✅ Пользователь {telegram_id} создан/обновлён")
                return result
                
            logger.error(f"❌ Не удалось создать/обновить пользователя {telegram_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя {telegram_id}: {e}")
            return None
    
    def update_user(self, telegram_id: int, username: str, first_name: str,
                    last_name: str = None, language_code: str = 'ru', 
                    chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Обновление данных пользователя"""
        try:
            update_data = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'language_code': language_code,
                'chat_id': chat_id,
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            # Убираем None значения
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = postgresql_client.update('users', {'telegram_id': telegram_id}, update_data)
            
            if result:
                logger.info(f"✅ Обновлен пользователь {telegram_id}")
                return result
            
            logger.warning(f"⚠️ Пользователь {telegram_id} не найден для обновления")
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя {telegram_id}: {e}")
            return None
    
    def get_or_create_user(self, telegram_id: int, username: str, first_name: str,
                           last_name: str = None, language_code: str = 'ru', 
                           chat_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Получить или создать пользователя"""
        try:
            # Сначала пытаемся получить пользователя
            user = self.get_user_by_telegram_id(telegram_id)
            
            if user:
                # Пользователь существует - обновляем
                updated = self.update_user(telegram_id, username, first_name, last_name, language_code, chat_id)
                return updated or user
            else:
                # Пользователь не существует - создаем
                return self.create_user(telegram_id, username, first_name, last_name, language_code, chat_id)
                
        except Exception as e:
            logger.error(f"❌ Ошибка в get_or_create_user для {telegram_id}: {e}")
            return None
    
    def delete_user(self, telegram_id: int) -> bool:
        """Удаление пользователя"""
        try:
            success = postgresql_client.delete('users', {'telegram_id': telegram_id})
            
            if success:
                logger.info(f"✅ Удален пользователь {telegram_id}")
                return True
            
            logger.warning(f"⚠️ Пользователь {telegram_id} не найден для удаления")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления пользователя {telegram_id}: {e}")
            return False
    
    def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение всех пользователей"""
        try:
            users = postgresql_client.select('users', limit=limit)
            logger.info(f"📊 Получено {len(users)} пользователей")
            return users
        except Exception as e:
            logger.error(f"❌ Ошибка получения всех пользователей: {e}")
            return []
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Получение активных пользователей"""
        try:
            # Используем count с фильтром
            cursor = postgresql_client._get_cursor()
            query = "SELECT * FROM users WHERE is_active = TRUE"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            active_users = [dict(row) for row in results]
            logger.info(f"📊 Получено {len(active_users)} активных пользователей")
            return active_users
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения активных пользователей: {e}")
            return []
    
    def update_user_field(self, telegram_id: int, field_name: str, field_value: Any) -> bool:
        """Обновление конкретного поля пользователя"""
        try:
            update_data = {
                field_name: field_value,
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            result = postgresql_client.update('users', {'telegram_id': telegram_id}, update_data)
            
            if result:
                logger.info(f"✅ Обновлено поле {field_name} для пользователя {telegram_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления поля {field_name} для пользователя {telegram_id}: {e}")
            return False
    
    def count_users(self) -> int:
        """Подсчет общего количества пользователей"""
        try:
            count = postgresql_client.count('users')
            logger.info(f"📊 Всего пользователей в базе: {count}")
            return count
        except Exception as e:
            logger.error(f"❌ Ошибка подсчета пользователей: {e}")
            return 0
    
    def check_user_exists(self, telegram_id: int) -> bool:
        """Проверка существования пользователя"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            return user is not None
        except Exception as e:
            logger.error(f"❌ Ошибка проверки существования пользователя {telegram_id}: {e}")
            return False

class UserSettingsCRUD:
    def get_settings(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            result = postgresql_client.select('user_settings', limit=1)
            for s in result:
                if s.get("telegram_id") == telegram_id:
                    return s
            return None
        except Exception as e:
            logger.error(f"Ошибка получения настроек пользователя {telegram_id}: {e}")
            return None

    def create_default_settings(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            settings_data = {
                'telegram_id': telegram_id,
                'notification_enabled': True,
                'daily_reminder_time': "09:00",
                'language_level': "beginner",
                'target_language': "en",
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'points': 0
            }
            result = postgresql_client.upsert('user_settings', settings_data, 'telegram_id')
            return result
        except Exception as e:
            logger.error(f"Ошибка создания настроек пользователя {telegram_id}: {e}")
            return None

    def update_notification_settings(self, telegram_id: int, enabled: bool) -> Optional[Dict[str, Any]]:
        try:
            settings = self.get_settings(telegram_id)
            if not settings:
                settings = self.create_default_settings(telegram_id)
                if not settings:
                    return None

            update_data = {
                'notification_enabled': enabled,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = postgresql_client.update('user_settings', {'telegram_id': telegram_id}, update_data)
            return result
        except Exception as e:
            logger.error(f"Ошибка обновления настроек уведомлений {telegram_id}: {e}")
            return None

user_crud = UserCRUD()
settings_crud = UserSettingsCRUD()