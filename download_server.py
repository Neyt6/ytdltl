from aiohttp import web
from urllib.parse import unquote, quote
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
VIDEO_DIR = BASE_DIR / "video"
PORT = int(os.getenv("DOWNLOAD_SERVER_PORT", "8000"))
PUBLIC_DOWNLOAD_BASE_URL=os.getenv("PUBLIC_DOWNLOAD_BASE_URL", "localhost")

APP = web.Application()
RUNNER = None
SITE = None


def _resolve_download_path(request: web.Request) -> Path | None:
    raw_path = unquote(request.rel_url.path)
    parts = [part for part in raw_path.split("/") if part]
    if len(parts) < 3 or parts[0] != "downloads":
        return None

    folder = parts[1]
    filename = "/".join(parts[2:])

    if folder == "audio":
        root = AUDIO_DIR
    elif folder == "video":
        root = VIDEO_DIR
    else:
        return None

    candidate = (root / filename).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None

    return candidate


async def download_handler(request: web.Request):
    target = _resolve_download_path(request)
    if target is None or not target.is_file():
        raise web.HTTPNotFound(text="File not found")

    safe_filename = quote(target.name, safe="")
    content_disposition = f"attachment; filename*=UTF-8''{safe_filename}"

    return web.FileResponse(
        path=target,
        chunk_size=8192,
        headers={
            "Content-Disposition": content_disposition,
        },
    )


APP.router.add_get("/downloads/{folder}/{filename:.*}", download_handler)


async def start_download_server():
    global RUNNER, SITE
    AUDIO_DIR.mkdir(exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)

    RUNNER = web.AppRunner(APP)
    await RUNNER.setup()
    SITE = web.TCPSite(RUNNER, "0.0.0.0", PORT)
    await SITE.start()

    print(f"Download server started at {PUBLIC_DOWNLOAD_BASE_URL}")


async def stop_download_server():
    global RUNNER, SITE
    if SITE is not None:
        await SITE.stop()
        SITE = None
    if RUNNER is not None:
        await RUNNER.cleanup()
        RUNNER = None


if __name__ == "__main__":
    import asyncio

    async def main():
        await start_download_server()
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await stop_download_server()

    asyncio.run(main())
