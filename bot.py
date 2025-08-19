import os
import logging
import pypandoc
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from .api_utils import cloudconvert_convert

# Локальные конвертерыle

# Тяжёлые через CloudConvert
# bot.py
from converters.api_utils import cloudconvert_convert
from converters.text import convert_text_file
from converters.audio import convert_audio_file
from converters.video import convert_video_file
from converters.image import convert_image_file
from converters.svg import convert_svg_file
from converters.pdf import convert_pdf_file


BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 10000))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
    # Устанавливаем вебхук
    await bot.set_webhook(WEBHOOK_URL)

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    return app

def convert_docx_to_pdf(input_file, output_file):
    pypandoc.convert_file(
        input_file,
        "pdf",  # формат выхода
        outputfile=output_file,
        extra_args=['--standalone']
    )
    return output_file


async def convert_pdf_file(file_path, target_format="docx"):
    return await cloudconvert_convert(file_path, target_format)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я конвертер файлов.\nПросто пришли мне документ.")

@dp.message()
async def handle_docs(message: types.Message):
    if not message.document:
        return await message.reply("📂 Пришлите файл для конвертации.")

    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_name = message.document.file_name
    file_ext = file_name.split(".")[-1].lower()

    os.makedirs("downloads", exist_ok=True)
    downloaded_path = f"downloads/{file_name}"
    await bot.download_file(file_path, downloaded_path)

    target_format = "pdf"  # ⚡ тестовый вариант — конвертируем всё в PDF

    try:
        if file_ext in ["txt", "docx", "rtf", "odt", "epub", "pdf"]:
            output_file = convert_text_file(downloaded_path, target_format)
        elif file_ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            output_file = convert_image_file(downloaded_path, target_format)
        elif file_ext == "svg":
            output_file = convert_svg_file(downloaded_path, target_format)
        elif file_ext in ["mp3", "wav", "ogg"]:
            output_file = convert_audio_file(downloaded_path, target_format)
        elif file_ext in ["mp4", "avi", "mkv"]:
            output_file = convert_video_file(downloaded_path, target_format)
        elif file_ext in ["zip", "rar", "7z"]:
            output_file = convert_archive_file(downloaded_path, target_format)
        elif file_ext in ["ttf", "otf", "woff"]:
            output_file = convert_font_file(downloaded_path, target_format)
        else:
            return await message.reply("❌ Этот формат пока не поддерживается.")

        if output_file:
            await message.reply_document(FSInputFile(output_file))
            os.remove(output_file)
        else:
            await message.reply("❌ Ошибка при конвертации.")

    except Exception as e:
        await message.reply(f"⚠️ Ошибка: {e}")

if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=PORT)