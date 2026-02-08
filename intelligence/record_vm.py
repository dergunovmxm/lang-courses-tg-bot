import tempfile
import subprocess
import os
import shutil
from aiogram.types import Voice

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHISPER_CPP_PATH = os.path.join(PROJECT_ROOT, 'intelligence', "whisper.cpp")
MODEL_NAME = "large-v3-turbo-q5_0"

if os.name == "nt":
    WHISPER_EXECUTABLE = os.path.join(WHISPER_CPP_PATH, "build", "bin", "Release", "whisper-cli.exe")
else:
    WHISPER_EXECUTABLE = os.path.join(WHISPER_CPP_PATH, "build", "bin", "whisper-cli")


async def transcribe_audio_v2(bot, voice: Voice) -> str:
    """
    Скачивает голосовое сообщение из Telegram (OGG/Opus),
    конвертирует его в WAV с помощью opusdec,
    и распознаёт текст через локальный whisper.cpp.
    Требует установленный opusdec (из пакета opus-tools).
    """
    # Проверяем наличие opusdec один раз при вызове
    if not shutil.which("opusdec"):
        raise RuntimeError(
            "Утилита opusdec не найдена. "
            "Установите opus-tools: "
            "macOS → brew install opus-tools, "
            "Ubuntu/Debian → sudo apt install opus-tools"
        )

    # Получаем информацию о файле
    file_info = await bot.get_file(voice.file_id)

    # Создаём временный .ogg файл
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
        tmp_ogg_path = tmp_ogg.name
        file_bytes = await bot.download_file(file_info.file_path)
        tmp_ogg.write(file_bytes.read())

    # Путь к выходному .wav файлу
    tmp_wav_path = tmp_ogg_path.replace(".ogg", ".wav")

    try:
        # Конвертация OGG/Opus → WAV с помощью opusdec
        subprocess.run(["opusdec", tmp_ogg_path, tmp_wav_path], check=True)

        # Путь к модели Whisper
        model_path = os.path.join(WHISPER_CPP_PATH, "models", f"ggml-{MODEL_NAME}.bin")

        # Команда для запуска whisper-cli
        cmd_whisper = [
            WHISPER_EXECUTABLE,
            "-m", model_path,
            "-l", "en",
            "--no-timestamps",
            "-f", tmp_wav_path
        ]

        # Запуск распознавания
        res = subprocess.run(cmd_whisper, capture_output=True, text=True)
        text = res.stdout.strip()

        return text

    finally:
        # Удаляем временные файлы в любом случае
        for path in (tmp_ogg_path, tmp_wav_path):
            if os.path.exists(path):
                os.remove(path)
                