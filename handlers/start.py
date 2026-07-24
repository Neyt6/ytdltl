import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram.types import Message, FSInputFile, CallbackQuery
from pathlib import Path
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from urllib.parse import quote
from ytdl import download_audio_youtube, download_video_youtube
from config import PUBLIC_DOWNLOAD_BASE_URL
import os

router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent

URL_RE = re.compile(r"^(https?://\S+)$", re.IGNORECASE)
MAX_TELEGRAM_FILE_SIZE_BYTES = 50 * 1024 * 1024


def is_url_text(text: str) -> bool:
    if not isinstance(text, str):
        return False
    return bool(URL_RE.fullmatch(text.strip()))


class Form(StatesGroup):
    audio_url = State()
    video_url = State()


def get_public_download_url(path: str) -> str | None:
    if not PUBLIC_DOWNLOAD_BASE_URL:
        return None

    file_path = Path(path)
    base_url = PUBLIC_DOWNLOAD_BASE_URL.rstrip("/")
    safe_folder = quote(file_path.parent.name, safe="")
    safe_filename = quote(file_path.name, safe="")
    return f"{base_url}/{safe_folder}/{safe_filename}"


async def send_media_or_download_link(message: Message, media_type: str, path: str) -> bool:
    if not path or not os.path.exists(path):
        return True

    file_size = os.path.getsize(path)
    if file_size > MAX_TELEGRAM_FILE_SIZE_BYTES:
        download_url = get_public_download_url(path)
        if download_url:
            await message.answer(
                f"📦 Файл больше 50 МБ, поэтому отправляю ссылку на скачивание:\n{download_url}"
            )
            return False

        await message.answer(
            "📦 Файл больше 50 МБ, но публичная ссылка для скачивания не настроена. "
            "Добавьте `PUBLIC_DOWNLOAD_BASE_URL` в окружение."
        )
        return True

    if media_type == "audio":
        await message.answer_audio(FSInputFile(path))
    else:
        await message.answer_video(FSInputFile(path))

    return True


@router.message(Command("start"))
async def start(message: Message):

    builder = ReplyKeyboardBuilder()

    builder.button(text="Скачать видео")
    builder.button(text="Скачать аудио")

    await message.answer(
        "Что сделать?",
        reply_markup=builder.as_markup(
            resize_keyboard=True
        )
    )


@router.message(F.text == "Скачать аудио")
async def get_audio_url(message: Message, state: FSMContext):
    await message.answer("Дай ссылку")
    await state.set_state(Form.audio_url)


@router.message(Form.audio_url)
async def download_audio(message: Message, state: FSMContext, deleteFile=True):
    url = message.text
    path = None
    should_delete = True

    try:
        await message.answer("Начинаю качать аудио...")
        path = await download_audio_youtube(url)
        should_delete = await send_media_or_download_link(message, "audio", path)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()
        if deleteFile and should_delete and path and os.path.exists(path):
            os.remove(path)


@router.message(F.text == "Скачать видео")
async def get_video_url(message: Message, state: FSMContext):
    await message.answer("Дай ссылку")
    await state.set_state(Form.video_url)


@router.message(F.text.regexp(URL_RE.pattern), StateFilter(None))
async def download_video_link(message: Message, state: FSMContext):
    url = message.text.strip()
    path = None
    should_delete = True

    try:
        await message.answer("Получена ссылка, качаю видео...")
        path = await download_video_youtube(url)
        should_delete = await send_media_or_download_link(message, "video", path)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        if should_delete and path and os.path.exists(path):
            os.remove(path)


@router.message(Form.video_url)
async def download_video(message: Message, state: FSMContext, deleteFile=True):
    url = message.text
    path = None
    should_delete = True

    try:
        await message.answer("Начинаю качать видео...")
        path = await download_video_youtube(url)
        should_delete = await send_media_or_download_link(message, "video", path)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()
        if deleteFile and should_delete and path and os.path.exists(path):
            os.remove(path)
