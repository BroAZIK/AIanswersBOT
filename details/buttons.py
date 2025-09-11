from telegram import InlineKeyboardButton 

short_but = [
        [InlineKeyboardButton("Short✅", callback_data="short"), InlineKeyboardButton("Medium", callback_data="medium"), InlineKeyboardButton("Complete", callback_data="complete")], 
        ]

medium_but = [
        [InlineKeyboardButton("Short", callback_data="short"), InlineKeyboardButton("Medium✅", callback_data="medium"), InlineKeyboardButton("Complete", callback_data="complete")], 
        ]

complete_but = [
        [InlineKeyboardButton("Short", callback_data="short"), InlineKeyboardButton("Medium", callback_data="medium"), InlineKeyboardButton("Complete✅", callback_data="complete")], 
        ]

channel_but = [
        [InlineKeyboardButton("A'zo bo'lish➕", url="https://t.me/iqmate_news")],
        [InlineKeyboardButton("Tekshirish✅", callback_data="check")]
]