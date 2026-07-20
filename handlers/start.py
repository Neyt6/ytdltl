from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from pathlib import Path
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from ytdl import download_audio_youtube, download_video_youtube
import os

router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


class Form(StatesGroup):
    audio_url = State()
    video_url = State()


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

    try:
        await message.answer("Начинаю качать аудио...")
        path = await download_audio_youtube(url)
        audio = FSInputFile(path)
        await message.answer_audio(audio)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()
        if (deleteFile):
            os.remove(path)


@router.message(F.text == "Скачать видео")
async def get_video_url(message: Message, state: FSMContext):
    await message.answer("Дай ссылку")
    await state.set_state(Form.video_url)


@router.message(Form.video_url)
async def download_video(message: Message, state: FSMContext, deleteFile=True):
    url = message.text

    try:
        await message.answer("Начинаю качать видео...")
        path = await download_video_youtube(url)
        video = FSInputFile(path)
        await message.answer_video(video)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()
        if (deleteFile):
            os.remove(path)
