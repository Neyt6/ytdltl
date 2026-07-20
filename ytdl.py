import yt_dlp
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Создаём директории если их нет
Path("./audio").mkdir(exist_ok=True)
Path("./video").mkdir(exist_ok=True)

executor = ThreadPoolExecutor(max_workers=2)


COMMON_OPTS = {
    "js_runtimes": {
        "node": {},
    },
}


def _download_audio_sync(url):
    """Синхронная функция загрузки аудио"""
    download_dir = "./audio"

    ydl_opts = {
        **COMMON_OPTS,
        "format": "bestaudio/best",
        "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if "requested_downloads" in info:
            filepath = info["requested_downloads"][0]["filepath"]
        else:
            filepath = ydl.prepare_filename(info)

    return filepath


async def download_audio_youtube(url):
    """Асинхронная загрузка аудио"""
    try:
        loop = asyncio.get_running_loop()
        filepath = await loop.run_in_executor(executor, _download_audio_sync, url)
        return filepath
    except Exception as e:
        raise Exception(f"Ошибка при загрузке аудио: {e}")


def _download_video_sync(url):
    """Синхронная функция загрузки видео"""
    download_dir = "./video"

    ydl_opts = {
        **COMMON_OPTS,
        "format": "best[ext=mp4]/best",
        "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if "requested_downloads" in info:
            filepath = info["requested_downloads"][0]["filepath"]
        else:
            filepath = ydl.prepare_filename(info)

    return filepath


async def download_video_youtube(url):
    """Асинхронная загрузка видео"""
    try:
        loop = asyncio.get_running_loop()
        filepath = await loop.run_in_executor(executor, _download_video_sync, url)
        return filepath
    except Exception as e:
        raise Exception(f"Ошибка при загрузке видео: {e}")
