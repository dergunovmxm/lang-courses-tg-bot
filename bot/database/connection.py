import psycopg2
from psycopg2.extras import RealDictCursor
from bot.config import config
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class PostgreSQLClient:
    def __init__(self):
        self.host = config.POSTGRESQL_HOST
        self.port = config.POSTGRESQL_PORT
        self.user = config.POSTGRESQL_USER
        self.password = config.POSTGRESQL_PASSWORD
        self.dbname = config.POSTGRESQL_DBNAME
        self.connection = None
        self.is_connected = False
        self._connect()
    
    def _connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            self.is_connected = True
            logger.info("✅ Успешное подключение к PostgreSQL")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            self.is_connected = False
    
    def test_connection(self):
        """Тестирование подключения к PostgreSQL"""
        try:
            if not self.is_connected:
                return False
            
            # Простой запрос для проверки соединения
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования подключения: {e}")
            # Попробуем переподключиться
            self._connect()
            return self.is_connected
    
    def close(self):
        """Закрытие соединения"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.is_connected = False
            logger.info("✅ Соединение с PostgreSQL закрыто")
    

    def _get_cursor(self):
        """Получение курсора"""
        if not self.is_connected or self.connection.closed:
            self._connect()
        return self.connection.cursor(cursor_factory=RealDictCursor)
    
    def insert(self, table: str, data: dict) -> Optional[Dict]:
        """Вставка данных"""
        if not self.is_connected:
            return None
        
        try:
            cursor = self._get_cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())
            
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f'✅ Вставка в {table} успешна')
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Ошибка вставки: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def select(self, table: str, limit: int = 15) -> List[Dict]:
        """Выборка данных"""
        try:
            cursor = self._get_cursor()
            query = f"SELECT * FROM {table} LIMIT %s"
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"❌ Ошибка выборки: {e}")
            print(f"❌ Ошибка выборки: {e}")
            return []
    
    def update(self, table: str, filters: Dict[str, Any], data: dict) -> Optional[Dict]:
        """Обновление данных"""
        if not self.is_connected:
            return None
        
        try:
            cursor = self._get_cursor()
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            set_values = list(data.values())
            
            where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
            where_values = list(filters.values())
            
            all_values = set_values + where_values
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause} RETURNING *"
            
            cursor.execute(query, all_values)
            result = cursor.fetchone()
            
            self.connection.commit()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Ошибка обновления: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """Удаление данных"""
        if not self.is_connected:
            return False
        
        try:
            cursor = self._get_cursor()
            where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
            where_values = list(filters.values())
            
            query = f"DELETE FROM {table} WHERE {where_clause}"
            cursor.execute(query, where_values)
            
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def count(self, table: str, filters: Dict[str, Any] = None) -> int:
        """Подсчет записей"""
        if not self.is_connected:
            return 0
        
        try:
            cursor = self._get_cursor()
            query = f"SELECT COUNT(*) as count FROM {table}"
            params = []
            
            if filters:
                where_clause = ' AND '.join([f"{key} = %s" for key in filters.keys()])
                query += f" WHERE {where_clause}"
                params = list(filters.values())
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Ошибка подсчета: {e}")
            return 0


postgresql_client = PostgreSQLClient()