import asyncio
import tempfile
from typing import Optional
from pathlib import Path
from aiogram import Bot
from aiogram.types import Voice

_WHISPER_MODEL_CACHE = {}
_WHISPER_MODEL_LOCK = asyncio.Lock()


async def transcribe_audio_v2(
    bot: Bot,
    voice: Voice,
    model_name: str = "base",  
    language: str = "en",
    compute_type: str = "int8"
) -> str:

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("pip install faster-whisper")

    temp_path: Optional[Path] = None

    try:
        temp_path = await _download_voice(bot, voice)
        model = await _load_model(model_name, compute_type)
        return await _transcribe(model, temp_path, language)

    except Exception as e:
        return _format_error(e, model_name)

    finally:
        await _cleanup(temp_path)


async def _download_voice(bot: Bot, voice: Voice) -> Path:
    """Скачивает голосовое сообщение во временный файл."""
    def _download():
        fd, path = tempfile.mkstemp(suffix=".ogg")
        import os
        os.close(fd)
        return Path(path)
    
    temp_path = await asyncio.to_thread(_download)
    await bot.download(voice, destination=temp_path)
    return temp_path


async def _load_model(model_name: str, compute_type: str):
    """Загружает модель с кэшированием."""
    from faster_whisper import WhisperModel

    cache_key = f"{model_name}_{compute_type}"
    async with _WHISPER_MODEL_LOCK:
        if cache_key not in _WHISPER_MODEL_CACHE:
            _WHISPER_MODEL_CACHE[cache_key] = await asyncio.to_thread(
                WhisperModel,
                model_name,
                device="auto",
                compute_type=compute_type,
                cpu_threads=2, 
                num_workers=1   
            )
        return _WHISPER_MODEL_CACHE[cache_key]


async def _transcribe(model, file_path: Path, language: str) -> str:
    """Транскрибирует аудиофайл."""
    def _run():
        segments, _ = model.transcribe(
            str(file_path),
            language=None if language == "auto" else language,
            beam_size=1, 
            best_of=1,    
            temperature=0, 
            vad_filter=True,
            vad_parameters={
                "threshold": 0.4, 
                "min_silence_duration_ms": 300  
            },
            
            condition_on_previous_text=False,
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6
        )
        return " ".join(seg.text for seg in segments).strip()

    return await asyncio.to_thread(_run)


async def _cleanup(path: Optional[Path]):
    """Удаляет временный файл."""
    if not path:
        return

    def _unlink():
        if not path.exists():
            return
        try:
            path.unlink()
        except Exception:
            pass

    await asyncio.to_thread(_unlink)


def _format_error(error: Exception, model_name: str) -> str:
    """Форматирует сообщение об ошибке."""
    msg = str(error)
    if "CUDA" in msg or "out of memory" in msg.lower():
        return f"(Ошибка GPU: недостаточно памяти)"
    if "not found" in msg.lower():
        return f"(Модель '{model_name}' не найдена)"
    return f"(Ошибка: {msg})"

                