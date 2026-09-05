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
    "extractor_args": {
        "youtube": {
            "player_client": ["android"],
        },
    },
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.youtube.com/",
    },
    "retries": 10,
    "fragment_retries": 10,
}


def _get_existing_download_path(url, download_dir, ydl_opts):
    probe_opts = {
        **ydl_opts,
        "skip_download": True,
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(probe_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            generated_path = ydl.prepare_filename(info)
    except Exception:
        return None

    stem = Path(generated_path).stem
    for candidate in sorted(Path(download_dir).glob(f"{stem}.*")):
        if candidate.is_file() and candidate.suffix.lower() not in {".part", ".f248", ".f251", ".tmp"}:
            return str(candidate)

    return None


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

    existing_path = _get_existing_download_path(url, download_dir, ydl_opts)
    if existing_path:
        return existing_path

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
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
        "quiet": False,
        "no_warnings": False,
    }

    existing_path = _get_existing_download_path(url, download_dir, ydl_opts)
    if existing_path:
        return existing_path

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
