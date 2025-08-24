import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from settings import TOKEN
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app yaratish
flask_app = Flask(__name__)

# Telegram Bot Application yaratish
try:
    telegram_app = Application.builder().token(TOKEN).build()
    logger.info("Telegram app muvaffaqiyatli yaratildi")
except Exception as e:
    logger.error(f"Telegram app yaratishda xatolik: {e}")
    telegram_app = None

if telegram_app:
    # Handlerlarni Telegram app ga qo'shish
    telegram_app.add_handler(CallbackQueryHandler(button_callbacks))
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("about", stats))
    telegram_app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    telegram_app.add_handler(MessageHandler(filters.PHOTO, photo))
    logger.info("Barcha handlerlar qo'shildi")

# Webhook endpoint
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if request.method == "POST":
            json_data = request.get_json(force=True)
            logger.info(f"Qabul qilingan ma'lumot: {json_data}")
            
            update = Update.de_json(json_data, telegram_app.bot)
            telegram_app.update_queue.put_nowait(update)
            logger.info("Update queue ga qo'shildi")
            
        return "OK"
    except Exception as e:
        logger.error(f"Webhook da xatolik: {e}")
        return "Error", 500

# Webhook ni o'rnatish
@flask_app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        webhook_url = f"https://iqmatebot.pythonanywhere.com/webhook"
        
        # Sync usulda webhook ni o'rnatish
        success = telegram_app.bot.set_webhook(webhook_url)
        
        if success:
            logger.info(f"Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
            return f"✅ Webhook o'rnatildi: {webhook_url}"
        else:
            logger.error("Webhook o'rnatish muvaffaqiyatsiz tugadi")
            return "❌ Webhook o'rnatish muvaffaqiyatsiz tugadi"
            
    except Exception as e:
        logger.error(f"Webhook o'rnatishda xatolik: {e}")
        return f"❌ Xatolik: {e}"

# Webhook ni o'chirish
@flask_app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    try:
        success = telegram_app.bot.delete_webhook()
        if success:
            return "✅ Webhook o'chirildi"
        else:
            return "❌ Webhook o'chirish muvaffaqiyatsiz"
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Webhook ma'lumotlarini ko'rish
@flask_app.route('/webhook_info', methods=['GET'])
def webhook_info():
    try:
        info = telegram_app.bot.get_webhook_info()
        return f"Webhook ma'lumotlari: {info}"
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Asosiy sahifa
@flask_app.route('/')
def index():
    return """
    <h1>Telegram Bot</h1>
    <p>Bot ishlamoqda!</p>
    <ul>
        <li><a href="/set_webhook">Webhook ni o'rnatish</a></li>
        <li><a href="/delete_webhook">Webhook ni o'chirish</a></li>
        <li><a href="/webhook_info">Webhook ma'lumotlari</a></li>
    </ul>
    """

# Botni ishga tushirish
def main():
    logger.info("Bot ishga tushmoqda...")
    flask_app.run(debug=True)

if __name__ == "__main__":
    main()
