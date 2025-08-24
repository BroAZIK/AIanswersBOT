import os
import logging
import asyncio
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

# Global application o'zgaruvchisi
telegram_app = None

# Har bir funksiya uchun alohida sync wrapper yaratish
def create_async_to_sync(async_func):
    def sync_func(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    return sync_func

# Botni ishga tushirish
def initialize_bot():
    global telegram_app
    try:
        # Telegram Bot Application yaratish
        telegram_app = Application.builder().token(TOKEN).build()
        logger.info("Telegram app muvaffaqiyatli yaratildi")

        # Handlerlarni Telegram app ga qo'shish
        telegram_app.add_handler(CallbackQueryHandler(button_callbacks))
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CommandHandler("about", stats))
        telegram_app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
        telegram_app.add_handler(MessageHandler(filters.PHOTO, photo))
        logger.info("Barcha handlerlar qo'shildi")

        # Application ni ishga tushirish
        telegram_app.initialize()
        logger.info("Telegram app initialized")

        return True
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
        return False

# Webhook endpoint
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not telegram_app:
            logger.error("Telegram app ishga tushmagan")
            return "Error: Bot not initialized", 500

        if request.method == "POST":
            json_data = request.get_json(force=True)
            logger.info(f"Qabul qilingan ma'lumot")
            
            update = Update.de_json(json_data, telegram_app.bot)
            
            # To'g'ridan-to'g'ri process_update ni chaqiramiz
            process_update_sync(update)
            logger.info("Update muvaffaqiyatli qayta ishlandi")
            
        return "OK"
    except Exception as e:
        logger.error(f"Webhook da xatolik: {e}")
        return "Error", 500

# Update ni qayta ishlash (sync versiya)
def process_update_sync(update):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(telegram_app.process_update(update))
    except Exception as e:
        logger.error(f"Update ni qayta ishlashda xatolik: {e}")
    finally:
        loop.close()

# Webhook ni o'rnatish
@flask_app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        if not telegram_app:
            return "Bot not initialized", 500
            
        webhook_url = f"https://iqmatebot.pythonanywhere.com/webhook"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(telegram_app.bot.set_webhook(webhook_url))
            
            if success:
                logger.info(f"Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
                return f"✅ Webhook o'rnatildi: {webhook_url}"
            else:
                logger.error("Webhook o'rnatish muvaffaqiyatsiz tugadi")
                return "❌ Webhook o'rnatish muvaffaqiyatsiz tugadi"
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Webhook o'rnatishda xatolik: {e}")
        return f"❌ Xatolik: {e}"

# Webhook ni o'chirish
@flask_app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    try:
        if not telegram_app:
            return "Bot not initialized", 500
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(telegram_app.bot.delete_webhook())
            if success:
                return "✅ Webhook o'chirildi"
            else:
                return "❌ Webhook o'chirish muvaffaqiyatsiz"
        finally:
            loop.close()
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Webhook ma'lumotlarini ko'rish
@flask_app.route('/webhook_info', methods=['GET'])
def webhook_info():
    try:
        if not telegram_app:
            return "Bot not initialized", 500
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            info = loop.run_until_complete(telegram_app.bot.get_webhook_info())
            return f"Webhook ma'lumotlari: {info.to_dict()}"
        finally:
            loop.close()
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
try:
    initialize_bot()
    logger.info("Bot muvaffaqiyatli ishga tushdi")
except Exception as e:
    logger.error(f"Botni ishga tushirib bo'lmadi: {e}")

if __name__ == "__main__":
    flask_app.run(debug=True)
