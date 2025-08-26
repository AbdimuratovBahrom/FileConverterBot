import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

from converters.api_utils import cloudconvert_convert

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # твой Render URL + /webhook/{token}

app = FastAPI()

# Установка вебхука при старте
@app.on_event("startup")
async def startup_event():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"}
        )
        print("Webhook set:", r.json())


@app.post("/webhook/{token}")
async def webhook_handler(token: str, request: Request):
    if token != BOT_TOKEN:
        return JSONResponse({"ok": False, "error": "invalid token"}, status_code=403)

    update = await request.json()
    print("Update:", update)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text.startswith("/convert"):
            try:
                input_file = "example.docx"   # тестовый входной файл
                output_file = "example.pdf"

                await cloudconvert_convert(input_file, output_file)

                await send_message(chat_id, "✅ Конвертация завершена! Файл сохранён.")
            except Exception as e:
                await send_message(chat_id, f"❌ Ошибка: {e}")
        else:
            await send_message(chat_id, "Привет! Отправь /convert для теста.")

    return JSONResponse({"ok": True})


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )
