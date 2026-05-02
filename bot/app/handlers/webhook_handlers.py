from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
logger = logging.getLogger(__name__)
load_dotenv()

webhook_router = APIRouter(
    prefix="/webhook",
    tags=["Webhooks"]
)

API_KEY = os.getenv('WEBHOOK_API_KEY')


class StudentInfo(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: str
    
    @field_validator('user_id')
    @classmethod
    def user_id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('user_id должен быть положительным')
        return v


class AnswerInfo(BaseModel):
    text: Optional[str] = None
    file_id: Optional[str] = None
    file_type: Optional[Literal['photo', 'document']] = None
    
    @field_validator('file_type')
    @classmethod
    def file_type_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['photo', 'document']:
            raise ValueError('file_type должен быть "photo" или "document"')
        return v


class NewAnswerData(BaseModel):
    session_id: str
    session_title: str
    student: StudentInfo
    answer: AnswerInfo
    submitted_at: str
    
    @field_validator('submitted_at')
    @classmethod
    def validate_submitted_at(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('submitted_at должен быть в формате ISO 8601')
        return v


class NewAnswerPayload(BaseModel):
    event: Literal['new_answer']
    data: NewAnswerData
    
    @model_validator(mode='after')
    @classmethod
    def validate_event_type(cls, model: 'NewAnswerPayload') -> 'NewAnswerPayload':
        if model.event != 'new_answer':
            raise ValueError(f'Неподдерживаемое событие: {model.event}')
        return model


class TaskNotificationData(BaseModel):
    session_id: str
    session_title: str
    task_text: str
    task_file_id: Optional[str] = None
    task_file_type: Optional[Literal['photo', 'document']] = None
    deadline: Optional[str] = None
    students: list[Dict[str, Any]]  # Список студентов для рассылки


class TaskNotificationPayload(BaseModel):
    event: Literal['new_task']
    data: TaskNotificationData
    
    @model_validator(mode='after')
    @classmethod
    def validate_event_type(cls, model: 'TaskNotificationPayload') -> 'TaskNotificationPayload':
        if model.event != 'new_task':
            raise ValueError(f'Неподдерживаемое событие: {model.event}')
        return model


async def get_admin_telegram_id(session_id: str) -> Optional[int]:

    from bot.database.lobby_crud import SessionCRUD
    
    try:
        crud = SessionCRUD()
        session = crud.get_session_by_id(session_id)
        
        if not session:
            logger.warning(f"⚠️ Лобби не найдено в БД: {session_id}")
            return None
        
        admin_id = session.creator_telegram_id
        
        if not admin_id:
            logger.warning(f"⚠️ У лобби {session_id} не указан creator_telegram_id")
            return None
        
        logger.info(f"✅ Найден админ {admin_id} для лобби {session_id}")
        return admin_id
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения админа для лобби {session_id}: {e}")
        return None
    
    


async def get_bot_instance(request: Request):
    try:
        bot = request.app.state.bot
        if bot:
            return bot
        logger.error("❌ Бот не инициализирован в app.state")
        return None
    except AttributeError:
        logger.error("❌ app.state.bot не существует")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка получения бота: {e}")
        return None


@webhook_router.post("/new_answer")
async def handle_new_answer(
    request: Request,
    payload: NewAnswerPayload,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):

    if API_KEY and x_api_key != API_KEY:
        logger.warning(f"⚠️ Неверный API-ключ: {x_api_key}")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )

    bot = await get_bot_instance(request)
    if not bot:
        logger.warning("⚠️ Бот не инициализирован — ответ не будет отправлен (сеть)")
        # Для продакшена:
        # raise HTTPException(status_code=500, detail="Bot not initialized")
  
    data = payload.data
    session_id = data.session_id
    session_title = data.session_title
    student = data.student
    answer = data.answer
    submitted_at = data.submitted_at
    
    logger.info(
        f"📝 Новый ответ: лобби={session_id}, "
        f"студент={student.user_id}, время={submitted_at}"
    )
    
  
    admin_telegram_id = await get_admin_telegram_id(session_id)
    
    if not admin_telegram_id:
        logger.error(f"❌ Не найден админ для лобби {session_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Admin not found for session {session_id}"
        )
  
    try:
        formatted_time = datetime.fromisoformat(
            submitted_at.replace('Z', '+00:00')
        ).strftime("%d.%m.%Y %H:%M")
    except Exception:
        formatted_time = submitted_at[:16].replace('T', ' ')
    
    username = f"@{student.username}" if student.username else "Без username"
    header = (
        f"📝 **Новый ответ в лобби «{session_title}»**\n\n"
        f"👤 От: {username} ({student.first_name})\n"
        f"⏰ Когда: {formatted_time}\n\n"
        f"📄 **Текст ответа:**\n"
        f"{'─' * 40}\n"
    )
    
    if answer.text:
        body = answer.text[:1000]
        if len(answer.text) > 1000:
            body += "\n\n... (продолжение)"
    else:
        body = "_(без текстового комментария)_"
    
    full_message = header + body
      
    if bot:
        try:
            if answer.file_id and answer.file_type:
                if answer.file_type == 'photo':
                    await bot.send_photo(
                        chat_id=admin_telegram_id,
                        photo=answer.file_id,
                        caption=full_message,
                        parse_mode="Markdown"
                    )
                elif answer.file_type == 'document':
                    await bot.send_document(
                        chat_id=admin_telegram_id,
                        document=answer.file_id,
                        caption=full_message,
                        parse_mode="Markdown"
                    )
            else:
                await bot.send_message(
                    chat_id=admin_telegram_id,
                    text=full_message,
                    parse_mode="Markdown"
                )
            
            logger.info(
                f"✅ Ответ от {student.user_id} переслан "
                f"админу {admin_telegram_id}"
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки ответа админу: {e}")
   
    return {
        "status": "received",
        "message": "Answer forwarded to admin",
        "session_id": session_id,
        "student_id": student.user_id,
        "admin_id": admin_telegram_id
    }

#Новое задание для рассылки

@webhook_router.post("/new_task")
async def handle_new_task(
    request: Request,
    payload: TaskNotificationPayload,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
     
    if API_KEY and x_api_key != API_KEY:
        logger.warning(f"⚠️ Неверный API-ключ: {x_api_key}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    bot = await get_bot_instance(request)
    if not bot:

        logger.warning("⚠️ Бот не инициализирован — рассылка не будет отправлена (сеть)")
        # Для продакшена:
        # raise HTTPException(status_code=500, detail="Bot not initialized")
    
    data = payload.data
    session_id = data.session_id
    session_title = data.session_title
    task_text = data.task_text
    task_file_id = data.task_file_id
    task_file_type = data.task_file_type
    deadline = data.deadline
    students = data.students
    
    logger.info(
        f"📚 Новое задание: лобби={session_id}, "
        f"студентов={len(students)}"
    )

    message_text = (
        f"📚 **Новое задание в лобби «{session_title}»**\n\n"
        f"{task_text}"
    )
    
    if deadline:
        try:
            # Конвертируем в строку если это datetime объект
            if isinstance(deadline, datetime):
                deadline_str = deadline.isoformat()
            else:
                deadline_str = deadline
            deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            message_text += f"\n\n⏰ **Дедлайн:** {deadline_dt.strftime('%d.%m.%Y %H:%M')}"
        except Exception:
            pass
    success_count = 0
    fail_count = 0
    
    if bot:
        for student in students:
 
            student_id = (
                student.get('user_id') 
                if isinstance(student, dict) 
                else getattr(student, 'user_id', None)
            )
            if not student_id:
                fail_count += 1
                continue
            
            try:

                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text="✍️ Выполнить",
                        callback_data=f"task_start_{session_id}"
                    )
                ]])
     
                if task_file_id and task_file_type:
                    if task_file_type == 'photo':
                        await bot.send_photo(
                            chat_id=student_id,
                            photo=task_file_id,
                            caption=message_text,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                    elif task_file_type == 'document':
                        await bot.send_document(
                            chat_id=student_id,
                            document=task_file_id,
                            caption=message_text,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                else:
                    await bot.send_message(
                        chat_id=student_id,
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                
                success_count += 1
                
            except Exception as e:
                logger.error(
                    f"❌ Не удалось отправить задание студенту {student_id}: {e}"
                )
                fail_count += 1
        
        logger.info(
            f"✅ Задание разослано: успешно={success_count}, "
            f"ошибок={fail_count}"
        )

    return {
        "status": "received",
        "message": "Task notifications sent",
        "session_id": session_id,
        "students_notified": success_count,
        "students_failed": fail_count
    }


@webhook_router.get("/health")
async def webhook_health_check():
    return {
        "status": "healthy",
        "service": "webhook_handler",
        "timestamp": datetime.now().isoformat()
    }