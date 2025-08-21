from telegram import Update, Bot, ParseMode, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    
    
)
from .api_requests import *
from details.database.db import *
from details.messages import *
from details.buttons import *
from pprint import pprint

bot = Bot(token="8473456433:AAFu9z8ZNi4fWfoBpo78STSiGbvahRQ8SCw")


def log_saver(user_id, full_name,  text, rassm=None):
    if rassm != None:
        bot.send_photo(chat_id=CHANNEL_ID, photo=rassm, caption=f"{text}\n\n <a href='tg://user?id={user_id}'>{full_name}</a> tomonidan yuborildi", parse_mode=ParseMode.HTML)
        insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})

    else:
        bot.send_message(chat_id=CHANNEL_ID, text=f"{text}\n\n <a href='tg://user?id={user_id}'>{full_name}</a> tomonidan yuborildi", parse_mode=ParseMode.HTML)
        insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})
    print("loglar muammosiz jo'natildi")

def start(update: Update, context):
    user_id = update.message.chat_id
    full_name = update.effective_chat.full_name
    
    insert(table="users", user_id=user_id, data={
            "name": full_name,
            "mode": "medium"
        })

    update.message.reply_text(
        text=start_message
    )

    mode = get(table="users", user_id=user_id)['mode']
    
    if mode == "short":
        update.message.reply_text(
        text=choice_mode_text,
        reply_markup=InlineKeyboardMarkup(short_but)
        )
    if mode == "complete":
        update.message.reply_text(
        text=choice_mode_text,
        reply_markup=InlineKeyboardMarkup(complete_but)
        )    
    
    if mode == "medium":
        update.message.reply_text(
        text=choice_mode_text,
        reply_markup=InlineKeyboardMarkup(medium_but)
        )
def text(update: Update, context):

    user_id = update.message.chat_id
    xabar = update.message.text
    mode = get(table="users", user_id=user_id)['mode']

    print("text ishlavotti")

    ai_text = ai_request(text=f"user.{user_id} | {xabar} | mode.{mode}")
    log_saver(user_id=user_id, full_name=update.effective_chat.full_name, text=xabar, rassm=None)


    if mode == "short":
        update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(short_but)
        )
    if mode == "medium":
        update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(medium_but)
        )
    if mode == "complete":
        update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(complete_but)
        )

def button_callbacks(update: Update, context):
    print(0)
    query = update.callback_query
    user_id = query.from_user.id
    # pprint(query.to_dict())
    mode = get(table="users", user_id=user_id)['mode']
    print(1)
    if query.data != mode:
        print(2)
        if query.data == "short":
            print(3)
            upd(table="users", user_id=user_id, data={"mode": "short"})
            query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(short_but))
        if query.data == "medium":
            upd(table="users", user_id=user_id, data={"mode": "medium"})
            query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(medium_but))
        if query.data == "complete":
            upd(table="users", user_id=user_id, data={"mode": "complete"})
            query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(complete_but))

        query.answer("✅Rejim o'zgardi", show_alert=True)
    else:
        print(4)
        query.answer("Boshqa rejimni tanlang❗️", show_alert=False)

def photo(update: Update, context):
    rasm = update.message.photo[-1].file_id
    tg_file = context.bot.get_file(rasm)
    file_path = tg_file.file_path
    user_id = update.effective_chat.id
    mode = get(table="users", user_id=user_id)['mode']

    print("rasm qabul qilindi")
    ocr_text = OCRres(file_path)
    print("OCR dan xabar keldi")

    log_saver(user_id=user_id, full_name=update.effective_chat.full_name, text=ocr_text, rassm=rasm)

    ai_text = ai_request(text=f"user.{user_id} | {ocr_text} | mode.{mode}")
    print("ai dan xabar keldi")


    if mode == "short":
        update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(short_but)
        )
    if mode == "medium":
        update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(medium_but)
        )
    if mode == "complete":
        update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(complete_but)
        )


def ignore_channel_posts(update, context):
    print("ignor qilindi")
    return



        
