# bot.py
# Main orchestrator — aiogram v3 style
import asyncio
import os
import tempfile
import shutil
import uuid
from pathlib import Path
from typing import Dict, List

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart

# local modules
from image import convert_image
from svg import convert_svg
from audio import convert_audio
from video import convert_video, extract_audio_from_video
from text import convert_text
from archives import archive_extract_then_pack, archive_create_from_dir
from fonts import convert_font

# -------------- CONFIG --------------
TOKEN = os.getenv("TELEGRAM_TOKEN", "8184283774:AAHlX0xwOU-3eKJK7DRsUvhFGQQaC506cxM")
if TOKEN == "PUT_YOUR_TOKEN_HERE" or not TOKEN:
    raise RuntimeError("Укажи TELEGRAM_TOKEN в переменных окружения перед запуском.")

MAX_TELEGRAM_BYTES = 50 * 1024 * 1024  # 50 MB (Telegram limit for bots usually)
ALLOWED_VIDEO_TO_AUDIO = ("mp3", "aac", "m4a", "wav", "flac", "ogg")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# In-memory pending map: key -> metadata
PENDING: Dict[str, dict] = {}

# Supported sets (same as discussed)
IMG_IN = {"jpg","jpeg","png","gif","bmp","webp","tiff","svg"}
IMG_OUT = {"jpg","png","webp","gif"}
AUD_IN = {"mp3","wav","ogg","flac","aac","m4a"}
AUD_OUT = {"mp3","wav","ogg","flac"}
VID_IN = {"mp4","avi","mkv","mov","webm"}
VID_OUT = {"mp4","avi","mkv","webm"}
DOC_IN = {"doc","docx","pdf","odt","rtf","txt","ppt","pptx","xls","xlsx","epub","md","html"}
DOC_OUT = {"pdf","docx","txt","odt"}
ARC_IN = {"zip","7z","rar","tar","gz"}
ARC_OUT = {"zip","7z","tar","gz"}
FONT_IN = {"ttf","otf","woff","woff2","eot"}
FONT_OUT = {"ttf","otf","woff"}

def available_targets(ext: str) -> List[str]:
    e = ext.lower()
    if e in IMG_IN:
        return sorted(list(IMG_OUT - {e}))
    if e in AUD_IN:
        return sorted(list(AUD_OUT - {e}))
    if e in VID_IN:
        return sorted(list(VID_OUT - {e})) + list(ALLOWED_VIDEO_TO_AUDIO)
    if e in DOC_IN:
        return sorted(list(DOC_OUT - ({e} if e in DOC_OUT else set())))
    if e in ARC_IN:
        return sorted(list(ARC_OUT - ({e} if e in ARC_OUT else set())))
    if e in FONT_IN:
        return sorted(list(FONT_OUT - {e}))
    return []

def short_key() -> str:
    return uuid.uuid4().hex[:16]

async def edit_safe(msg: types.Message, text: str):
    try:
        await msg.edit_text(text)
    except Exception:
        pass

# ---------- /start handler ----------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Начать", callback_data="start_flow")
    kb.adjust(1)
    tools_text = (
        "Отправь файл — я предложу форматы для конвертации.\n\n"
        "Поддерживается: документы, изображения, svg, аудио, видео, архивы, шрифты.\n"
        "Ограничение Telegram: файлы до 50 MB."
    )
    await message.answer(tools_text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "start_flow")
async def cb_start_flow(call: CallbackQuery):
    await call.answer("Готов! Пришли файл.")
    await call.message.answer("Пришли файл (документ/изображение/аудио/видео/архив/шрифт).")

# ---------- File intake ----------
@dp.message(F.document | F.photo | F.audio | F.video)
async def on_file(message: Message):
    try:
        # create tmp dir
        tempd = Path(tempfile.mkdtemp(prefix="fconv_"))
        if message.photo:
            f = message.photo[-1]
            file_info = await bot.get_file(f.file_id)
            filename = f"photo_{message.message_id}.jpg"
        elif message.document:
            f = message.document
            file_info = await bot.get_file(f.file_id)
            filename = f.file_name or f"file_{message.message_id}"
        elif message.audio:
            f = message.audio
            file_info = await bot.get_file(f.file_id)
            filename = f.file_name or f"audio_{message.message_id}.mp3"
        elif message.video:
            f = message.video
            file_info = await bot.get_file(f.file_id)
            filename = f.file_name or f"video_{message.message_id}.mp4"
        else:
            await message.reply("⚠️ Неподдерживаемый тип файла.")
            return

        size = getattr(f, "file_size", None)
        if size and size > MAX_TELEGRAM_BYTES:
            await message.reply(f"❌ Файл слишком большой (> {MAX_TELEGRAM_BYTES//1024//1024} MB).")
            return

        status = await message.reply("⬇️ Загружаю файл...")
        file_bytes = await bot.download_file(file_info.file_path)
        input_path = tempd / filename
        # file_bytes is aioHTTP stream-like: we read as bytes
        data = file_bytes.read()
        input_path.write_bytes(data)

        ext = input_path.suffix.lower().lstrip(".")
        targets = available_targets(ext)
        if not targets:
            await status.edit_text("⚠️ Этот тип файла пока не поддерживается.")
            shutil.rmtree(tempd, ignore_errors=True)
            return

        key = short_key()
        PENDING[key] = {"tempdir": str(tempd), "input": str(input_path), "ext": ext, "chat_id": message.chat.id}

        kb = InlineKeyboardBuilder()
        for t in targets:
            kb.button(text=f"→ {t.upper()}", callback_data=f"cv|{key}|{t}")
        kb.adjust(3)
        await status.edit_text(f"✅ Файл получен: <b>{input_path.name}</b>\nВыберите формат:", parse_mode="HTML")
        await message.answer("Выберите формат:", reply_markup=kb.as_markup())

    except Exception as e:
        await message.reply(f"❌ Ошибка при загрузке файла: {e}")

# ---------- Conversion callback ----------
@dp.callback_query(F.data.startswith("cv|"))
async def on_convert(call: CallbackQuery):
    await call.answer("Запускаю конвертацию…")
    try:
        _, key, target = call.data.split("|", 2)
    except ValueError:
        return
    meta = PENDING.get(key)
    if not meta:
        await call.message.answer("⚠️ Данные устарели — пришлите файл снова.")
        return

    chat_id = meta["chat_id"]
    tempd = Path(meta["tempdir"])
    input_path = Path(meta["input"])
    src_ext = meta["ext"]

    status_msg = await call.message.answer("🔁 Конвертация запущена… Подождите...")
    # run conversion in background
    asyncio.create_task(process_and_send(chat_id, status_msg, input_path, src_ext, target, tempd, key))

async def process_and_send(chat_id: int, status_msg: types.Message, input_path: Path,
                           src_ext: str, target: str, tempd: Path, key: str):
    try:
        out_name = f"{input_path.stem}_to_{target}.{target}"
        output_path = tempd / out_name

        def do_convert_sync():
            # images
            if src_ext in IMG_IN and target in IMG_OUT:
                if src_ext == "svg":
                    return convert_svg(input_path, output_path)
                return convert_image(input_path, output_path, target)
            # audio
            if src_ext in AUD_IN and target in AUD_OUT:
                return convert_audio(input_path, output_path, target)
            # video -> video
            if src_ext in VID_IN and target in VID_OUT:
                return convert_video(input_path, output_path, target)
            # video -> audio
            if src_ext in VID_IN and target in ALLOWED_VIDEO_TO_AUDIO:
                return extract_audio_from_video(input_path, output_path, target)
            # documents / text
            if src_ext in DOC_IN and target in DOC_OUT:
                return convert_text(input_path, output_path, target)
            # archives
            if src_ext in ARC_IN and target in ARC_OUT:
                # extract then pack
                extract_dir = tempd / "extracted"
                ok = archive_extract_then_pack(input_path, extract_dir, target, output_path)
                return ok
            # fonts
            if src_ext in FONT_IN and target in FONT_OUT:
                return convert_font(input_path, output_path, target)
            return False

        ok = await asyncio.get_event_loop().run_in_executor(None, do_convert_sync)

        if not ok or not output_path.exists():
            await edit_safe(status_msg, "❌ Конвертация для этого типа файла пока не реализована или произошла ошибка.")
            return

        size = output_path.stat().st_size
        if size > MAX_TELEGRAM_BYTES:
            await edit_safe(status_msg, f"❌ Результат слишком большой для Telegram ({size//1024//1024} MB).")
            return

        await bot.send_document(chat_id, types.FSInputFile(str(output_path), filename=output_path.name),
                                caption=f"Готово — {output_path.name} ({size//1024//1024} MB)")
        await edit_safe(status_msg, "✅ Конвертация завершена.")
    except Exception as e:
        await edit_safe(status_msg, f"❌ Ошибка конвертации: {e}")
    finally:
        try:
            shutil.rmtree(tempd, ignore_errors=True)
        except Exception:
            pass
        PENDING.pop(key, None)

# ---------- Run ----------
async def on_startup():
    print("Bot started...")

if __name__ == "__main__":
    asyncio.run(on_startup())
    dp.run_polling(bot)
