from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from bot.database.lobby_crud import SessionCRUD, SessionMembersCRUD
from bot.database.lobby_models import Session, SessionMember
from datetime import datetime, timezone
import uuid
import logging
from typing import Optional, List
import os
logger = logging.getLogger(__name__)


lobby_router = APIRouter(
    prefix="/api/lobbies",
    tags=["Lobbies"]
)
class CloseLobbyRequest(BaseModel):
    user_id: int
class CreateLobbyRequest(BaseModel):
    title: str         
    user_id: int            
    username: str          
    first_name: str    

class JoinLobbyRequest(BaseModel):
    invite_code: str        
    user_id: int           
    username: str           
    first_name: str         

class LeaveLobbyRequest(BaseModel):
    session_id: str         
    user_id: int           

class CreateTaskRequest(BaseModel):
    text: str                          
    file_id: Optional[str] = None      
    file_type: Optional[str] = None    
    deadline: Optional[str] = None    
    user_id: int 

class SubmitAnswerRequest(BaseModel):
    answer_text: Optional[str] = None  
    answer_file_id: Optional[str] = None  
    answer_file_type: Optional[str] = None  
    user_id: int
class TaskResponse(BaseModel):
    session_id: str
    text: str
    file_id: Optional[str]
    file_type: Optional[str]
    deadline: Optional[str]
    created_at: str
    is_active: bool
@lobby_router.post("/create")
async def create_lobby(request: CreateLobbyRequest):
    logger.info(f"📝 Создание лобби: {request.title}")
    
    crud = SessionCRUD()
    session_id = f"lobby_{uuid.uuid4().hex[:8]}"
    invite_code = None
    for _ in range(30):
        code = f"LOB{uuid.uuid4().hex[:6].upper()}"      
        if not crud.get_session_by_invite_code(code):
            invite_code = code
            break  
        if not invite_code:
                raise HTTPException(status_code=500, detail="Не удалось сгенерировать уникальный код. Попробуйте позже.")
    session = Session(
        session_id=session_id,
        creator_id=request.user_id,
        creator_telegram_id=request.user_id,
        created_at=datetime.now().isoformat(),
        title=request.title,
        invite_code=invite_code
    )
    
    created_session = crud.create_session(session)
    
    if not created_session:
        logger.error("❌ Ошибка создания лобби")
        raise HTTPException(status_code=500, detail="Ошибка создания лобби")
    
    members_crud = SessionMembersCRUD()
    member = SessionMember(
        user_id=request.user_id,
        session_id=created_session.session_id,
        role='admin',
        username=request.username,
        first_name=request.first_name
    )

    added_member = members_crud.add_member(member)
    if not added_member:
        logger.error(f"❌ Не удалось добавить админа в лобби: {request.user_id}")
        raise HTTPException(status_code=500, detail="Ошибка добавления участника")
    logger.info(f"✅ Лобби создано: {created_session.session_id}")


    
    return {
        "status": "success",
        "message": "Лобби создано",
        "lobby": created_session.to_dict()
    }

@lobby_router.post("/join")
async def join_lobby(request: JoinLobbyRequest):
 
    logger.info(f"📥 Вступление в лобби: {request.invite_code}")
    
    crud = SessionCRUD()
    
    session = crud.get_session_by_invite_code(request.invite_code)
    
    if not session:
        logger.warning(f"❌ Лобби не найдено: {request.invite_code}")
        raise HTTPException(status_code=404, detail="Лобби не найдено")
    
    members_crud = SessionMembersCRUD()
    
    existing = members_crud.get_member(session.session_id, request.user_id)
    if existing:
        logger.warning(f"⚠️ Пользователь уже в лобби: {request.user_id}")
        raise HTTPException(status_code=400, detail="Вы уже в этом лобби")
    
    member = SessionMember(
        user_id=request.user_id,
        session_id=session.session_id,
        role='student',
        username=request.username,
        first_name=request.first_name
    )
    added_member = members_crud.add_member(member)
    if not added_member:
        logger.error(f"❌ Не удалось добавить участника: {request.user_id}")
        raise HTTPException(status_code=500, detail="Ошибка вступления в лобби")
    
    logger.info(f"✅ Пользователь вступил: {request.user_id} → {session.session_id}")
    
    return {
        "status": "success",
        "message": "Вы вступили в лобби",
        "lobby": session.to_dict()
    }

@lobby_router.post("/leave")
async def leave_lobby(request: LeaveLobbyRequest):
   
    logger.info(f"📤 Выход из лобби: {request.session_id}")
    
    members_crud = SessionMembersCRUD()
    result = members_crud.remove_member(request.session_id, request.user_id)
    
    if not result:
        logger.error(f"❌ Не удалось покинуть лобби: {request.session_id}")
        raise HTTPException(status_code=400, detail="Не удалось покинуть лобби")
    
    logger.info(f"✅ Пользователь вышел: {request.user_id} из {request.session_id}")
    
    return {
        "status": "success",
        "message": "Вы покинули лобби"
    }

@lobby_router.get("/my/{user_id}")
async def get_my_lobbies(user_id: int):
    logger.info(f"📋 Получение лобби пользователя: {user_id}")
    
    members_crud = SessionMembersCRUD()
    crud = SessionCRUD()
    
    session_ids = members_crud.get_sessions_by_user_id(user_id)
    
    lobbies = []
    for session_id in session_ids:
        session = crud.get_session_by_id(session_id)
        if session and session.is_active:
            lobbies.append({
                "session_id": session.session_id,
                "title": session.title,
                "invite_code": session.invite_code,
                "is_active": session.is_active,
                "created_at": session.created_at,
            })
    
    return {
        "status": "success",
        "lobbies": lobbies
    }


@lobby_router.post("/{session_id}/tasks")
async def create_task(session_id: str, request: CreateTaskRequest):
#ток для админа лобби
    logger.info(f"📝 Создание задания в лобби: {session_id}")
    
    crud = SessionCRUD()
    members_crud = SessionMembersCRUD()
    session = crud.get_session_by_id(session_id)
    if not session:
        logger.warning(f"❌ Лобби не найдено: {session_id}")
        raise HTTPException(status_code=404, detail="Лобби не найдено")
    if not session.is_active:
        raise HTTPException(status_code=404, detail="Лобби не найдено или закрыто")
    
    if session.creator_telegram_id != request.user_id:
        
        member = members_crud.get_member(session_id, request.user_id)
        
        if not member or member.role != 'admin':
            logger.warning(f"⚠️ Пользователь {request.user_id} не админ лобби {session_id}")
            raise HTTPException(status_code=403, detail="Только админ может создавать задания")
    
    update_data = {
        'active_task_text': request.text,
        'active_task_file_id': request.file_id,      
        'active_task_file_type': request.file_type,  
        'active_task_deadline': request.deadline,    
        'active_task_created_at': datetime.now().isoformat(),
        'is_active': True
    }
    
    updated_session = crud.update_session(session_id, update_data)
    
    if not updated_session:
        logger.error(f"❌ Ошибка обновления задания в лобби: {session_id}")
        raise HTTPException(status_code=500, detail="Ошибка сохранения задания")
    
    logger.info(f"✅ Задание создано в лобби: {session_id}")
    deadline = getattr(updated_session, 'active_task_deadline', None)
    if deadline and isinstance(deadline, datetime):
        deadline = deadline.isoformat()
    bot_payload = {
        "event": "new_task",
        "data": {
            "session_id": updated_session.session_id,
            "session_title": updated_session.title,
            "task_text": updated_session.active_task_text,
            "task_file_id": getattr(updated_session, 'active_task_file_id', None),
            "task_file_type": getattr(updated_session, 'active_task_file_type', None),
            "deadline": deadline,
            "students": [
                {
                    "user_id": member.user_id,
                    "username": member.username,
                    "first_name": member.first_name
                }
                for member in members_crud.get_all_members(session_id)
                if member.role == 'student'  # Только ученикам, не админам
            ]
        }
    }

    BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL", "http://localhost:8000/webhook")
    WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY")

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BOT_WEBHOOK_URL}/new_task",
                json=bot_payload,
                headers={"X-API-Key": WEBHOOK_API_KEY}
            )
            if response.status_code != 200:
                logger.warning(f"⚠️ Бот не подтвердил рассылку: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки вебхука боту: {e}")

  
    return {
        "status": "success",
        "message": "Задание создано",
        "task": {
            "session_id": updated_session.session_id,
            "text": updated_session.active_task_text,
            "file_id": getattr(updated_session, 'active_task_file_id', None),
            "file_type": getattr(updated_session, 'active_task_file_type', None),
            "deadline": getattr(updated_session, 'active_task_deadline', None),
            "created_at": updated_session.active_task_created_at,
            "is_active": updated_session.is_active
        }
    }

@lobby_router.get("/{session_id}/tasks")
async def get_task(session_id: str):
 
    logger.info(f"📖 Получение задания в лобби: {session_id}")
    
    crud = SessionCRUD()
    

    session = crud.get_session_by_id(session_id)
    if not session:
        logger.warning(f"❌ Лобби не найдено: {session_id}")
        raise HTTPException(status_code=404, detail="Лобби не найдено")
    if not session.is_active:
        raise HTTPException(status_code=404, detail="Лобби не найдено или закрыто") 
    if not session.active_task_text:
        logger.info(f"ℹ️ В лобби {session_id} нет активного задания")
        return {
            "status": "success",
            "task": None,
            "message": "Нет активного задания"
        }
    
    return {
        "status": "success",
        "task": {
            "session_id": session.session_id,
            "text": session.active_task_text,
            "file_id": getattr(session, 'active_task_file_id', None),
            "file_type": getattr(session, 'active_task_file_type', None),
            "deadline": getattr(session, 'active_task_deadline', None),
            "created_at": getattr(session, 'active_task_created_at', None),
            "is_active": session.is_active
        }
    }

@lobby_router.post("/{session_id}/tasks/submit")
async def submit_answer(session_id: str, request: SubmitAnswerRequest):

    logger.info(f"📝 Ответ от {request.user_id} в лобби {session_id}")
    
    crud = SessionCRUD()
    members_crud = SessionMembersCRUD()
    
    session = crud.get_session_by_id(session_id)
    if not session:
        logger.warning(f"❌ Лобби не найдено: {session_id}")
        raise HTTPException(status_code=404, detail="Лобби не найдено")
    if not session.is_active:
        raise HTTPException(status_code=404, detail="Лобби не найдено или закрыто")
    member = members_crud.get_member(session_id, request.user_id)
    if not member:
        logger.warning(f"⚠️ Пользователь {request.user_id} не участник лобби {session_id}")
        raise HTTPException(status_code=403, detail="Только участники лобби могут отправлять ответы")
    
    if not session.active_task_text:
        logger.warning(f"⚠️ В лобби {session_id} нет активного задания")
        raise HTTPException(status_code=400, detail="Нет активного задания")
    
    if session.active_task_deadline:
        deadline = datetime.fromisoformat(session.active_task_deadline)
        if datetime.now(timezone.utc) > deadline:
            logger.warning(f"⚠️ Дедлайн прошёл для задания в лобби {session_id}")
            raise HTTPException(status_code=400, detail="Срок выполнения задания истёк")
    

    
    logger.info(f"✅ Ответ получен от {request.user_id} в лобби {session_id}")

    bot_payload = {
        "event": "new_answer",
        "data": {
            "session_id": session_id,
            "session_title": session.title,
            "student": {
                "user_id": request.user_id,
                "username": member.username,
                "first_name": member.first_name
            },
            "answer": {
                "text": request.answer_text,
                "file_id": request.answer_file_id,
                "file_type": request.answer_file_type
            },
            "submitted_at": datetime.now().isoformat()
        }
    }
    
    BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL", "http://localhost:8000/webhook")
    WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY")
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BOT_WEBHOOK_URL}/new_answer",
                json=bot_payload,
                headers={"X-API-Key": WEBHOOK_API_KEY}
            )
            if response.status_code != 200:
                logger.warning(f"⚠️ Бот не подтвердил пересылку ответа: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки вебхука ответа: {e}")
    
    return {
        "status": "success",
        "message": "Ответ отправлен преподавателю",
        "submitted_at": datetime.now().isoformat()
    }

@lobby_router.delete("/{session_id}")
async def delete_session(session_id: str, request: CloseLobbyRequest = Body(...)):
    crud = SessionCRUD()
    session = crud.get_session_by_id(session_id)
    if not session:
        logger.warning(f"❌ Лобби не найдено: {session_id}")
        raise HTTPException(status_code=404, detail="Лобби не найдено")
    if request.user_id != session.creator_telegram_id:
        logger.warning(f"⚠️ Пользователь {request.user_id} не владелец лобби {session_id}")
        raise HTTPException(status_code=403, detail="Только владелец может удалять сессии")
    crud.update_session(session_id, {'is_active': False})
    return {"status": "success", "message": "Лобби закрыто", "session_id": session_id}
