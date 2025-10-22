import requests
from config import config
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.base_url = config.SUPABASE_URL
        self.api_key = config.SUPABASE_KEY
        self.headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        self.is_connected = False
        self._test_connection()
    
    def _test_connection(self):

        #Тестирование подключения к Supabase

        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/",
                headers={'apikey': self.api_key}
            )
            if response.status_code == 200:
                self.is_connected = True
                logger.info("✅ Успешное подключение к Supabase")
            else:
                logger.error(f"❌ Ошибка подключения: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Supabase: {e}")

    def test_connection(self):
        return self.is_connected
    
    def insert(self, table: str, data: dict) -> Optional[Dict]:

        #Вставка данных в таблицу

        if not self.is_connected:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/rest/v1/{table}",
                headers=self.headers,
                json=data
            )
            if response.status_code == 201:
                result = response.json()
                return result[0] if isinstance(result, list) and result else result
            else:
                logger.error(f"❌ Ошибка вставки в {table}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка вставки в {table}: {e}")
            return None
    
    def select(self, table: str, filters: Dict[str, Any] = None, limit: int = None, order: str = None) -> List[Dict]:

        #Выборка данных из таблицы
        
        if not self.is_connected:
            return []
        
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {}
            
            # Добавляем фильтры
            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"
            
            # Добавляем лимит
            if limit:
                params['limit'] = str(limit)
            
            # Добавляем сортировку
            if order:
                params['order'] = order
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Ошибка выборки из {table}: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"❌ Ошибка выборки из {table}: {e}")
            return []
    
    def update(self, table: str, filters: Dict[str, Any], data: dict) -> Optional[Dict]:

        #Обновление данных в таблице

        if not self.is_connected:
            return None
        
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {}
            
            # Добавляем фильтры
            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"
            
            response = requests.patch(
                url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result[0] if isinstance(result, list) and result else result
            else:
                logger.error(f"❌ Ошибка обновления в {table}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка обновления в {table}: {e}")
            return None
    
    def delete(self, table: str, filters: Dict[str, Any]) -> bool:

        #Удаление данных из таблицы
        
        if not self.is_connected:
            return False
        
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {}
            
            # Добавляем фильтры
            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"
            
            response = requests.delete(url, headers=self.headers, params=params)
            
            if response.status_code == 204:
                return True
            else:
                logger.error(f"❌ Ошибка удаления из {table}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка удаления из {table}: {e}")
            return False
    
    def count(self, table: str, filters: Dict[str, Any] = None) -> int:
        """Подсчет количества записей"""
        if not self.is_connected:
            return 0
        
        try:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {
                'select': 'count'
            }
            
            # Добавляем фильтры
            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"
            
            headers = self.headers.copy()
            headers['Prefer'] = 'count=exact'
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                # Supabase возвращает количество в заголовке
                count_header = response.headers.get('content-range')
                if count_header and '/' in count_header:
                    return int(count_header.split('/')[-1])
                return 0
            else:
                logger.error(f"❌ Ошибка подсчета в {table}: {response.status_code} - {response.text}")
                return 0
        except Exception as e:
            logger.error(f"❌ Ошибка подсчета в {table}: {e}")
            return 0

# Глобальный экземпляр клиента
supabase_client = SupabaseClient()