import sys
from pathlib import Path
import requests
from promt import promt_system, generate_random_task, generate_audio_task
import json
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
import bot.database.connection 
from bot.config import config
url = 'https://api.deepseek.com/v1/chat/completions'
ai_key = config.API_DEEPSEEK
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ai_key}",  
}

data = {
    'model': 'deepseek-reasoner',  
    'messages': [
        {'role': 'system', 'content': promt_system},
        {'role': 'user', 'content': generate_audio_task()}
    ],
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    text = result['choices'][0]['message']['content']
    task_data = json.loads(text)
    task_data["variants"] = json.dumps(task_data["variants"])
    
    bot.database.connection.postgresql_client.insert('tasks', task_data)
    print(text)
else:
    print(f"Ошибка: {response.status_code}")
    print(response.text)