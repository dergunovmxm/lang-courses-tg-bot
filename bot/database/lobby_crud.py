from datetime import datetime
from typing import Optional, List, Dict, Any
from bot.database.lobby_models import Session, SessionMember
from bot.database.connection import postgresql_client
import logging

logger = logging.getLogger(__name__)
class SessionCRUD:
    def create_session(self, session:Session) -> Optional[Session]:
        try:
            result = postgresql_client.insert('sessions', session.to_dict())
            if result:
                logger.info(f"✅ Сессия создана: {result['session_id']}")
                return Session.from_dict(result)
        except Exception as e:
            logger.error(f"❌ Ошибка создания сессии: {e}")
            return None
    def get_session_by_id(self, session_id:str) -> Optional[Session]:
        try: 
            result = postgresql_client.select('sessions', f"session_id = '{session_id}'")
            if result and len(result) > 0:
                return Session.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения сессии: {e}")
            return None
    def get_session_by_invite_code(self, invite_code:str) -> Optional[Session]:
        try:

            result = postgresql_client.select('sessions', f"invite_code = '{invite_code}'")
            if result and len(result) > 0:
                return Session.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения кода приглашения: {e}")
            return None
    def get_all_sessions(self, limit: int=100) -> List[Session]:
        try:
            result = postgresql_client.select('sessions', 'is_active = TRUE', limit=limit)
            return [Session.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка сессий: {e}")
            return []
    def update_session(self, session_id: str,  data:Dict[str, Any]) -> Optional[Session]:

        try:
            result = postgresql_client.update('sessions', {'session_id': session_id}, data)
            if result:
                logger.info(f"✅ Сессия обновлена: {session_id}")
                return Session.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка обновления сессии: {e}")
            return None
    def delete_session(self, session_id: str) -> bool:
        result = postgresql_client.delete('sessions', {'session_id':session_id})
        try:
            if result:
                logger.info(f"✅ Сессия удалена: {session_id}")
                return result
        except Exception as e:
            logger.error(f"❌ Ошибка удаления сессии: {e}")
            return False
    def get_expired_sessions(self, days: int=90):
        try:
            # ⚠️ SQL-запрос для поиска старых сессий
            query = f"""
                SELECT * FROM sessions 
                WHERE created_at < NOW() - INTERVAL '{days} days'
                AND is_active = TRUE
                """
            cursor = postgresql_client.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return [Session.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"❌ Ошибка получения устаревших сессий: {e}")
            return []
# ============================================================
# ИСПРАВЛЕННЫЙ КЛАСС SessionMembersCRUD
# ============================================================
class SessionMembersCRUD:
    def add_member(self, member: SessionMember) -> Optional[SessionMember]:
        try:
            # ✅ to_dict() теперь возвращает 'user_id', а не 'telegram_id'
            result = postgresql_client.insert('session_members', member.to_dict())
            if result:
                logger.info(f"✅ Участник добавлен: {member.username}")
                return SessionMember.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка добавления участника: {e}")
            return None
    
    def get_member(self, session_id: str, user_id: int) -> Optional[SessionMember]:
        try:
            # ✅ Одинарные кавычки для session_id, без кавычек для user_id (число)
            result = postgresql_client.select('session_members', f"session_id = '{session_id}' AND user_id = {user_id}")
            if result and len(result) > 0:
                return SessionMember.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения участника: {e}")
            return None
    
    def get_all_members(self, session_id: str) -> List[SessionMember]:
        try:
            # ✅ self добавлен, кавычки одинарные
            result = postgresql_client.select('session_members', f"session_id = '{session_id}'")
            return [SessionMember.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка участников: {e}")
            return []
    
    def remove_member(self, session_id: str, user_id: int) -> bool:
        try:
            result = postgresql_client.delete(
                'session_members', 
                {'session_id': session_id, 'user_id': user_id}
            )
            if result:
                logger.info(f"✅ Участник удалён: {user_id} из {session_id}")
            return result
        except Exception as e:
            logger.error(f"❌ Ошибка удаления участника: {e}")
            return False
    
    def update_member_role(self, session_id: str, user_id: int, new_role: str) -> Optional[SessionMember]:
        try:
            result = postgresql_client.update(
                'session_members',
                {'session_id': session_id, 'user_id': user_id},
                {'role': new_role}
            )
            if result:
                logger.info(f"✅ Роль обновлена: {user_id} → {new_role}")
                return SessionMember.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка обновления роли: {e}")
            return None
    def get_sessions_by_user_id(self, user_id: int) -> List[str]:
        try:
            cursor = postgresql_client._get_cursor()
            
            query = "SELECT session_id FROM session_members WHERE user_id = %s"
            cursor.execute(query, (user_id,)) 
            
            results = cursor.fetchall()
            cursor.close()
            
            return [row['session_id'] for row in results]
                    
        except Exception as e:
            logger.error(f'❌ Ошибка получения списка сессий для пользователя {user_id}: {e}')
            return []
def cleanup_expired_sessions(days: int = 30) -> int:

    expired_sessions = SessionCRUD.get_expired_sessions(days)
    deleted_count = 0
    
    for session in expired_sessions:
        if SessionCRUD.delete_session(session.session_id):
            deleted_count += 1
    
    logger.info(f"🧹 Удалено {deleted_count} устаревших сессий")
    return deleted_count

        