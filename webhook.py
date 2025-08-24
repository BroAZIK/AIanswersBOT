from telegram import Bot
from settings import *

bot = Bot(TOKEN)

url = "https://YOURDOMAIN.com/webhook/" + TOKEN
print(bot.set_webhook(url))
