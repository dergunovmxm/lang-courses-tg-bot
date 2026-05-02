from datetime import datetime
from typing import Optional, Dict, Any
class Session:
    def __init__(self, 
                 session_id: str,
                 creator_id: int,
                 creator_telegram_id: int,
                 created_at: str,              
                 title: str = '',
                 description: Optional[str] = None,
                 invite_code: str = '',
                 is_active: bool = True,
                 is_public: bool = False,
                 auto_notify: bool = True,
                 max_members: int = 100,
                 
                 active_task_text: Optional[str] = None,
                 active_task_created_at: Optional[str] = None,
                 active_task_deadline: Optional[str] = None,
                 
                 total_tasks_created: int = 0,
                 total_answers_received: int = 0,
                 
                 updated_at: Optional[str] = None,
                 last_activity_at: Optional[str] = None):
        self.session_id = session_id
        self.creator_id = creator_id
        self.creator_telegram_id = creator_telegram_id
        self.title = title
        self.description = description
        self.invite_code = invite_code
        self.is_active = is_active
        self.is_public = is_public
        self.auto_notify = auto_notify
        self.max_members = max_members
        self.total_tasks_created = total_tasks_created
        self.total_answers_received = total_answers_received
        self.active_task_text = active_task_text
        self.active_task_created_at = active_task_created_at
        self.active_task_deadline = active_task_deadline
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.last_activity_at = last_activity_at or datetime.now().isoformat()
    def to_dict(self) -> Dict[str, Any]:

        return {
            'session_id': self.session_id,
            'creator_id': self.creator_id,
            'creator_telegram_id': self.creator_telegram_id,
            'created_at': self.created_at,
            'title': self.title,
            'description': self.description,
            'invite_code': self.invite_code,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'auto_notify': self.auto_notify,
            'max_members': self.max_members,
            'active_task_text': self.active_task_text,
            'active_task_created_at': self.active_task_created_at,
            'active_task_deadline': self.active_task_deadline,
            'total_tasks_created': self.total_tasks_created,
            'total_answers_received': self.total_answers_received,
            'updated_at': self.updated_at,
            'last_activity_at': self.last_activity_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
 
        return cls(
            session_id=data.get('session_id', ''),
            creator_id=data.get('creator_id', 0),
            creator_telegram_id=data.get('creator_telegram_id', 0),
            created_at=data.get('created_at', datetime.now().isoformat()),
            title=data.get('title', ''),
            description=data.get('description'),
            invite_code=data.get('invite_code', ''),
            is_active=data.get('is_active', True),
            is_public=data.get('is_public', False),
            auto_notify=data.get('auto_notify', True),
            max_members=data.get('max_members', 100),
            active_task_text=data.get('active_task_text'),
            active_task_created_at=data.get('active_task_created_at'),
            active_task_deadline=data.get('active_task_deadline'),
            total_tasks_created=data.get('total_tasks_created', 0),
            total_answers_received=data.get('total_answers_received', 0),
            updated_at=data.get('updated_at'),
            last_activity_at=data.get('last_activity_at')
        )
    def is_expired(self, days: int = 30) -> bool:
        try:
            created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            now = datetime.now()
            return (now - created).days > days
        except Exception:
            return True
class SessionMember:
    def __init__(self,
                 user_id: int,                    
                 session_id: str,
                 role: str = 'student',
                 username: Optional[str] = None,
                 first_name: Optional[str] = None,
                 is_active: bool = True,
                 is_banned: bool = False,
                 can_invite: bool = False,
                 can_create_tasks: bool = False,
                 joined_at: Optional[str] = None):
        
        self.user_id = user_id
        self.session_id = session_id
        self.role = role
        self.username = username
        self.first_name = first_name
        self.is_active = is_active
        self.is_banned = is_banned
        self.can_invite = can_invite
        self.can_create_tasks = can_create_tasks
        self.joined_at = joined_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для PostgreSQL"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,              
            'role': self.role,
            'username': self.username,
            'first_name': self.first_name,
            'is_active': self.is_active,
            'is_banned': self.is_banned,
            'can_invite': self.can_invite,
            'can_create_tasks': self.can_create_tasks,
            'joined_at': self.joined_at
        }
    
    @classmethod
    def from_dict(cls,  data:Dict[str, Any]) -> 'SessionMember':
        """Создание объекта SessionMember из словаря PostgreSQL"""
        return cls(
            user_id=data.get('user_id', 0),     
            session_id=data.get('session_id', ''),
            role=data.get('role', 'student'),
            username=data.get('username'),
            first_name=data.get('first_name'),
            is_active=data.get('is_active', True),
            is_banned=data.get('is_banned', False),
            can_invite=data.get('can_invite', False),
            can_create_tasks=data.get('can_create_tasks', False),
            joined_at=data.get('joined_at')
        )