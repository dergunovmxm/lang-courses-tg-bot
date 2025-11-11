import sys
from pathlib import Path
import requests
from promt import promt_system, promt_user
import json
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
import database.supabase_client 
from config import config
url = 'https://api.intelligence.io.solutions/api/v1/chat/completions'
ai_key = config.API_DEEPSEEK
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ai_key}",  
}

data = {
    'model': 'deepseek-ai/DeepSeek-R1-0528',  
    'messages': [
        {'role': 'system', 'content': promt_system},
        {'role': 'user', 'content': promt_user}
    ],
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    text = result['choices'][0]['message']['content']
    task = text.split('</think>\n')[1]
    task_data = json.loads(task)
    database.supabase_client.supabase_client.insert('tasks', task_data)
    print(task)
else:
    print(f"Ошибка: {response.status_code}")
    print(response.text)