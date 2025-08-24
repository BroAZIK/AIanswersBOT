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
import threading
from settings import *
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats

app = Flask(__name__)

# Bot va Application yaratish
application = Application.builder().token(TOKEN).build()

# Handlerlarni qo'shish
application.add_handler(CallbackQueryHandler(button_callbacks))
application.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("about", stats))
application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
application.add_handler(MessageHandler(filters.PHOTO, photo))

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
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        # Async funksiyani sync qilib chaqiramiz
        process_update_sync(update)
    return "OK"

# Async funksiyani sync qilish
@async_to_sync
async def process_update_sync(update):
    await application.process_update(update)

# Webhook ni o'rnatish
@app.route('/set_webhook', methods=['GET', 'POST'])
@async_to_sync
async def set_webhook():
    webhook_url = f"https://{os.environ.get('PYTHONANYWHERE_SITE', 'yourusername.pythonanywhere.com')}/webhook"
    success = await application.bot.set_webhook(webhook_url)
    if success:
        return f"Webhook o'rnatildi: {webhook_url}"
    else:
        return "Webhook o'rnatishda xatolik"

# Asosiy sahifa
@app.route('/')
def index():
    return "Telegram Bot ishlamoqda!"

# Botni ishga tushirish
def run_bot():
    print("Bot ishga tushmoqda...")
    application.run_polling(
        allowed_updates=[Update.MESSAGE, Update.CALLBACK_QUERY],
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    # Flask ni ishga tushirish
    app.run(debug=True)
