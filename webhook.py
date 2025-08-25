from telegram import Bot
from settings import *

bot = Bot(token=TOKEN)


def get_info():
    """Webhook haqida ma'lumot olish"""
    info = bot.get_webhook_info()
    print("Webhook info:", info)


def delete():
    """Webhookni o‘chirish"""
    result = bot.delete_webhook()
    print("Webhook o‘chirildi:", result)


def set():
    """Webhookni sozlash"""
    url = f"https://iqmatebot.pythonanywhere.com/webhook/{TOKEN}"
    result = bot.set_webhook(url=url)
    print("Webhook o‘rnatildi:", result)


if __name__ == "__main__":
    # Birini tanlab ishlating
    # get_info()
    # delete()
    set()
