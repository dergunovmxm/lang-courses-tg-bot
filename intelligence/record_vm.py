# Файл: record_vm.py
import tempfile
import subprocess
import os
from aiogram.types import Voice
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHISPER_CPP_PATH = os.path.join(PROJECT_ROOT, 'intelligence', "whisper.cpp")
MODEL_NAME = "large-v3-turbo-q5_0"

if os.name == "nt":
    WHISPER_EXECUTABLE = os.path.join(WHISPER_CPP_PATH, "build", "bin", "Release", "whisper-cli.exe")
else:
    WHISPER_EXECUTABLE = os.path.join(WHISPER_CPP_PATH, "build", "bin", "whisper-cli")
async def transcribe_audio_v2(bot, voice: Voice) -> str:
    """
    Скачивает голосовое сообщение из Telegram в поток, конвертирует его в WAV
    и распознаёт текст с помощью локального Whisper (whisper.cpp).
    """
    # Получаем информацию о файле
    file_info = await bot.get_file(voice.file_id)
    
    # Создаем временный ogg файл
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
        tmp_ogg_path = tmp_ogg.name
        # Скачиваем файл напрямую в tmp_ogg
        file_bytes = await bot.download_file(file_info.file_path)
        tmp_ogg.write(file_bytes.read())

    # Создаем временный wav файл
    tmp_wav_path = tmp_ogg_path.replace(".ogg", ".wav")
    subprocess.run(["ffmpeg", "-y", "-i", tmp_ogg_path, tmp_wav_path], check=True)

    # Путь к локальному whisper-cli
    if os.name == "nt":
        whisper_executable = os.path.join(WHISPER_CPP_PATH, "build", "bin", "Release", "whisper-cli.exe")
    else:
        whisper_executable = os.path.join(WHISPER_CPP_PATH, "build", "bin", "whisper-cli")

    model_path = os.path.join(WHISPER_CPP_PATH, "models", f"ggml-{MODEL_NAME}.bin")

    # Запуск whisper для распознавания
    cmd_whisper = [
        whisper_executable,
        "-m", model_path,
        "-l", "ru",
        "--no-timestamps",
        "-f", tmp_wav_path
    ]

    res = subprocess.run(cmd_whisper, capture_output=True, text=True)
    text = res.stdout.strip()

    # Удаляем временные файлы
    os.remove(tmp_ogg_path)
    os.remove(tmp_wav_path)

    return text