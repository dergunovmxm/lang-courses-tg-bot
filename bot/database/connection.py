import psycopg2
from psycopg2.extras import RealDictCursor
from bot.config import config
import logging
from typing import Optional, List, Dict, Any, Union
import datetime
logger = logging.getLogger(__name__)
from psycopg2 import sql
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
    
    def select(self, table: str, condition: str | None = None, limit: int | None = None) -> List[Dict]:
        try:
            cursor = self._get_cursor()
            
            query = f"SELECT * FROM {table}"
            
            if condition:
                query += f" WHERE {condition}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"❌ Ошибка выборки: {e}")
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
    def get_random_task(self):
        try:
            cursor = self._get_cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY RANDOM() LIMIT 1")
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения рандомного задания: {e}")
            return None
    def get_task_by_level(self, level):
        try: 
            cursor = self._get_cursor()
            cursor.execute('SELECT * FROM tasks WHERE level = %s ORDER BY RANDOM() LIMIT 1;',
                           (level,))
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f'Ошибка получения задания уровня {level}: {e}')
            return None

    def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        conflict_columns: Union[str, List[str]],
        update_columns: Optional[List[str]] = None,
        returning: str = "*"
    ) -> Optional[Dict]:
        if not self.is_connected:
            return None

        try:
            cursor = self._get_cursor()

            # Нормализуем conflict_columns в список
            if isinstance(conflict_columns, str):
                conflict_columns = [conflict_columns]
            if update_columns is None:
                # Обновляем все поля, кроме конфликтующих
                update_columns = [col for col in data.keys() if col not in conflict_columns]

            # Экранируем имена таблиц и колонок
            columns = list(data.keys())
            col_identifiers = sql.SQL(', ').join(map(sql.Identifier, columns))
            val_placeholders = sql.SQL(', ').join(sql.Placeholder() * len(columns))
            table_ident = sql.Identifier(table)
            conflict_ident = sql.SQL(', ').join(map(sql.Identifier, conflict_columns))
            update_set = sql.SQL(', ').join(
                sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
                for col in update_columns
            )
            returning_clause = sql.SQL(returning)

            query = sql.SQL("""
                INSERT INTO {} ({})
                VALUES ({})
                ON CONFLICT ({})
                DO UPDATE SET {}
                RETURNING {};
            """).format(
                table_ident,
                col_identifiers,
                val_placeholders,
                conflict_ident,
                update_set,
                returning_clause
            )

            cursor.execute(query, list(data.values()))
            result = cursor.fetchone()
            self.connection.commit()
            cursor.close()

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"❌ Ошибка универсального upsert в {table}: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    def add_points(self, user_id: int, points: int) -> int:

        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (telegram_id, points)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id)
                DO UPDATE SET points = users.points + EXCLUDED.points
                RETURNING points
                """,
                (user_id, points)
            )
            new_points = cursor.fetchone()[0]
            self.connection.commit()
            return new_points
    def get_audio_task(self, level: str = None):
        try:
            cursor = self._get_cursor()
            if level:
                cursor.execute(
                    "SELECT * FROM tasks WHERE type = 'audio_question' AND level = %s ORDER BY RANDOM() LIMIT 1;",
                    (level,)
                )
            else:
                cursor.execute("SELECT * FROM tasks WHERE type = 'audio_question' ORDER BY RANDOM() LIMIT 1;")
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения аудиозадания: {e}")
            return None

postgresql_client = PostgreSQLClient()