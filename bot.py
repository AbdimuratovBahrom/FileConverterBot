import os
import tempfile
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from converters.text import convert_text_file
from converters.image import convert_image_file
from converters.audio import convert_audio_file
from converters.archive import extract_archive, create_archive
from converters.api_utils import cloudconvert_convert

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # пример: https://fileconverterbot-hanm.onrender.com/webhook

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = FastAPI()


# === Обработчик документов ===
@dp.message(F.document)
async def handle_file(message: Message):
    doc = message.document
    file_name = doc.file_name.lower()

    # Скачиваем файл
    file_path = os.path.join(tempfile.gettempdir(), file_name)
    await message.bot.download(doc, destination=file_path)

    ext = os.path.splitext(file_name)[1]

    try:
        # --- Текстовые ---
        if ext in [".docx", ".txt", ".md", ".rtf", ".odt", ".html", ".epub"]:
            out_file = convert_text_file(file_path, target_format="txt")
            await message.answer_document(open(out_file, "rb"))

        # --- Изображения ---
        elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".svg"]:
            out_file = convert_image_file(file_path, target_format="png")
            await message.answer_document(open(out_file, "rb"))

        # --- Архивы ---
        elif ext in [".zip", ".rar", ".7z"]:
            out_dir = extract_archive(file_path)
            new_zip = create_archive(out_dir, "zip")
            await message.answer_document(open(new_zip, "rb"))

        # --- PDF ---
        elif ext == ".pdf":
            out_file = cloudconvert_convert(file_path, "docx")
            await message.answer_document(open(out_file, "rb"))

        # --- Аудио ---
        elif ext in [".mp3", ".wav", ".ogg", ".flac", ".m4a"]:
            out_file = convert_audio_file(file_path, "wav")
            await message.answer_document(open(out_file, "rb"))

        # --- Видео ---
        elif ext in [".mp4", ".avi", ".mkv", ".webm", ".mov", ".wmv"]:
            out_file = cloudconvert_convert(file_path, "mp4")
            await message.answer_document(open(out_file, "rb"))

        else:
            await message.answer("❌ Неподдерживаемый формат!")

    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")


# === FastAPI маршруты ===
@app.get("/")
async def root():
    return {"status": "ok", "message": "File Converter Bot is running 🚀"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


# === Автоматическая установка вебхука ===
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    print("🚀 Bot started via webhook")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    print("🛑 Bot stopped")
