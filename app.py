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
import pytz
from settings import *
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats

app = Flask(__name__)

# Bot va Application yaratish
application = Application.builder().token(TOKEN).build()

# Handlerlarni qo'shish
application.add_handler(CallbackQueryHandler(button_callbacks))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("about", stats))
application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
application.add_handler(MessageHandler(filters.PHOTO, photo))

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "OK"

# Webhook ni o'rnatish
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    webhook_url = f"https://{os.environ.get('PYTHONANYWHERE_SITE')}.pythonanywhere.com/webhook"
    success = application.bot.set_webhook(webhook_url)
    if success:
        return f"Webhook o'rnatildi: {webhook_url}"
    else:
        return "Webhook o'rnatishda xatolik"

# Asosiy sahifa
@app.route('/')
def index():
    return "Telegram Bot ishlamoqda!"

if __name__ == "__main__":
    app.run(debug=True)
