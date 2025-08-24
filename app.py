import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import asyncio
from settings import *
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats

# Flask app yaratish
flask_app = Flask(__name__)

# Telegram Bot Application yaratish
telegram_app = Application.builder().token(TOKEN).build()

# Handlerlarni Telegram app ga qo'shish
telegram_app.add_handler(CallbackQueryHandler(button_callbacks))
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("about", stats))
telegram_app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
telegram_app.add_handler(MessageHandler(filters.PHOTO, photo))

# Async funksiyani sync qilish uchun wrapper
def async_to_sync(async_func):
    def sync_func(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    return sync_func

# Webhook endpoint (sync versiya)
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        # Async funksiyani sync qilib chaqiramiz
        process_update_sync(update)
    return "OK"

# Async funksiyani sync qilish
@async_to_sync
async def process_update_sync(update):
    await telegram_app.process_update(update)

# Webhook ni o'rnatish
@flask_app.route('/set_webhook', methods=['GET', 'POST'])
@async_to_sync
async def set_webhook():
    webhook_url = f"https://iqmatebot.pythonanywhere.com/webhook"
    success = await telegram_app.bot.set_webhook(webhook_url)
    if success:
        return f"Webhook o'rnatildi: {webhook_url}"
    else:
        return "Webhook o'rnatishda xatolik"

# Asosiy sahifa
@flask_app.route('/')
def index():
    return "Telegram Bot ishlamoqda!"

if __name__ == "__main__":
    flask_app.run(debug=True)
