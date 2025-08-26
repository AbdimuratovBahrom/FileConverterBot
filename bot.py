import os
import telebot
from fastapi import FastAPI, Request
from converters.api_utils import cloudconvert_convert

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = FastAPI()


# ==== Routes ====
@app.get("/")
def index():
    return {"status": "ok", "message": "Bot is running on Render"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.body()
    update = telebot.types.Update.de_json(data.decode("utf-8"))
    bot.process_new_updates([update])
    return {"status": "ok"}


# ==== Startup ====
@app.on_event("startup")
async def startup_event():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)


# ==== Bot handlers ====
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 Привет! Отправь файл, и я конвертирую его через CloudConvert.")


@bot.message_handler(content_types=["document"])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        # Пример: конвертация в pdf
        output_file = cloudconvert_convert(
            input_file_url=file_url,
            input_format=message.document.file_name.split(".")[-1],
            output_format="pdf",
            output_file="output.pdf"
        )

        with open(output_file, "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")
