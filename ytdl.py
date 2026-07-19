import yt_dlp


async def download_audio_youtube(url):
    download_dir = "./audio"
    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        # Шаблон пути и имени файла
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if "requested_downloads" in info:
            filepath = info["requested_downloads"][0]["filepath"]
        else:
            filepath = ydl.prepare_filename(info)

    return filepath


async def download_video_youtube(url):
    download_dir = "./video"
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if "requested_downloads" in info:
            filepath = info["requested_downloads"][0]["filepath"]
        else:
            filepath = ydl.prepare_filename(info)

    return filepath
