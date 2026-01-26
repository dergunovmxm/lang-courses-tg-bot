import sys
from pathlib import Path
import requests
import time
import json

# Настройка путей
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from promt import promt_system, generate_random_task
import bot.database.connection 
from bot.config import config

# Конфигурация API
url = 'https://api.deepseek.com/v1/chat/completions'  # ← исправлено: убраны лишние пробелы
ai_key = config.API_DEEPSEEK
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ai_key}",
}

# Сколько заданий сгенерировать
NUM_TASKS = 20 

print(f"🚀 Начинаем генерацию {NUM_TASKS} заданий (строгий режим: остановка при первой ошибке)...")

for i in range(NUM_TASKS):
    print(f"\n--- Шаг {i + 1}/{NUM_TASKS} ---")
    
    # 1. Формируем запрос
    data = {
        'model': 'deepseek-reasoner',
        'messages': [
            {'role': 'system', 'content': promt_system},
            {'role': 'user', 'content': generate_random_task()}
        ],
    }

    # 2. Отправляем запрос к API
    print("📡 Отправка запроса к нейросети...")
    response = requests.post(url, headers=headers, json=data, timeout=100)

    if response.status_code != 200:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: API вернул статус {response.status_code}")
        print("Тело ответа:", response.text)
        print("Остановка процесса.")
        sys.exit(1)  # Полная остановка

    # 3. Парсим ответ
    print("📄 Получен ответ, парсим JSON...")
    try:
        result = response.json()
        raw_text = result['choices'][0]['message']['content']
        task_data = json.loads(raw_text)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: не удалось распарсить ответ нейросети")
        print("Ответ:", raw_text)
        print("Ошибка:", e)
        print("Остановка процесса.")
        sys.exit(1)

    # 4. Подготавливаем данные для БД
    print("🛠️  Подготовка данных для вставки...")
    try:
        # Обязательные поля
        required = ["question", "answer", "level", "cost", "type"]
        for field in required:
            if field not in task_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")

        # Сериализуем variants
        if "variants" in task_data:
            if isinstance(task_data["variants"], list):
                task_data["variants"] = json.dumps(task_data["variants"], ensure_ascii=False)
            else:
                task_data["variants"] = json.dumps([])
        else:
            task_data["variants"] = json.dumps([])

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при подготовке данных: {e}")
        print("Остановка процесса.")
        sys.exit(1)

    # 5. Вставляем в базу данных
    print("💾 Вставка в базу данных...")
    try:
        bot.database.connection.postgresql_client.insert('tasks', task_data)
        print(f"✅ Успешно добавлено задание: {task_data['question'][:50]}...")
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при вставке в БД: {e}")
        print("Остановка процесса.")
        sys.exit(1)

    # Небольшая задержка перед следующим запросом (рекомендуется API)
    time.sleep(1.0)

print(f"\n🎉 Все {NUM_TASKS} заданий успешно сгенерированы и добавлены в базу данных!")