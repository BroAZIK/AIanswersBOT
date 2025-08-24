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


async def set():
    """Webhookni sozlash"""
    url = f"https://iqmatebot.pythonanywhere.com/webhook/{TOKEN}"
    result = await bot.set_webhook(url=url)
    print("Webhook o‘rnatildi:", result)


import asyncio

if __name__ == "__main__":
    # delete()  # agar sync bo'lsa
    asyncio.run(set())
