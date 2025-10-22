from datetime import datetime

bot_start_time = None

def set_bot_start_time():
    """Устанавливает время старта бота"""
    global bot_start_time
    bot_start_time = datetime.now()

def get_current_time():
    """Возвращает текущее время в читаемом формате"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_bot_uptime():
    """Возвращает время работы бота"""
    if bot_start_time is None:
        return "00:00:00"
    
    uptime = datetime.now() - bot_start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"