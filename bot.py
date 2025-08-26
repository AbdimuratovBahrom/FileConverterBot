import os
from dotenv import load_dotenv
from fastapi import FastAPI
import telebot

# Загружаем .env (для локального теста)
load_dotenv()

# Получаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан! Добавь его в Environment Variables на Render или в .env")

# Создаём объект бота
bot = telebot.TeleBot(BOT_TOKEN)

# FastAPI приложение
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("🚀 Стартап приложения...")
    # Безопасно удаляем старый webhook
    try:
        bot.remove_webhook()
        print("✅ Webhook успешно удалён")
    except Exception as e:
        print(f"⚠️ Не удалось удалить webhook: {e}")

@app.get("/")
async def root():
    return {"status": "Bot is running"}

# Пример ручки webhook (если используешь)
# Пример безопасного вызова webhook
@app.post("/webhook")
async def telegram_webhook(update: dict):
    from telebot.types import Update
    upd = Update.de_json(update)
    bot.process_new_updates([upd])  
    return {"ok": True}
