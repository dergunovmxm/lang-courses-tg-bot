import sys
from pathlib import Path
import requests
from promt import promt_system, generate_random_task
import json
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
import bot.database.connection 
from bot.config import config

text = '''{
  "id": 53,
  "created_at": "2025-11-08T12:00:00Z",
  "question": "Choose the correct form to complete the sentence: By the time she retires, she ______ in the company for over three decades.",
  "answer": "will have been working",
  "solution": "Future Perfect Continuous используется для выражения действия, которое началось до определенного момента в будущем и продолжается до этого момента, подчеркивая его продолжительность. В данном случае, 'by the time she retires' указывает на будущий момент, а 'for over three decades' — на длительность.",
  "theme": "Future Perfect Continuous",
  "type": "multiple_choice",
  "level": "C1",
  "variants": ["will have been working", "will be working", "will have worked", "will work"],
  "cost": 50
}'''


task_data = json.loads(text)
task_data["variants"] = json.dumps(task_data["variants"])
    
bot.database.connection.postgresql_client.insert('tasks', task_data)
print(text)
