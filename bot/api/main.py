
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot
import os
import logging
from dotenv import load_dotenv


load_dotenv()


from .lobby_routes import lobby_router
from bot.app.handlers.webhook_handlers import webhook_router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lang Courses API",
    description="API для управления лобби и заданиями",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(lobby_router)
app.include_router(webhook_router)

@app.on_event("startup")
async def startup_event():
 
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        logger.warning("⚠️ Вебхуки не смогут отправлять сообщения")
        return
    
    try:
        # Создаём экземпляр бота
        bot = Bot(token=token)
        
        app.state.bot = bot
        
        me = await bot.get_me()
        logger.info(f"✅ Бот инициализирован для вебхуков: @{me.username} (id: {me.id})")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        logger.warning("⚠️ Вебхуки не смогут отправлять сообщения")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Корректно закрывает сессию бота при остановке API.
    """
    if hasattr(app.state, "bot") and app.state.bot:
        try:
            await app.state.bot.session.close()
            logger.info("✅ Сессия бота закрыта")
        except Exception as e:
            logger.error(f"❌ Ошибка закрытия сессии бота: {e}")

@app.get("/")
def root():
    """Проверка, что API работает"""
    return {"message": "✅ Lang Courses API работает!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "healthy"}

@app.get("/health/bot")
async def bot_health_check(request: Request):
    """Проверка, что бот инициализирован"""
    if hasattr(app.state, "bot") and app.state.bot:
        return {"status": "healthy", "bot": "initialized"}
    return {"status": "degraded", "bot": "not_initialized"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)