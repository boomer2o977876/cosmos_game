from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 /top", callback_data="menu:top"),
         InlineKeyboardButton(text="✈️ /flight", callback_data="menu:flight")],
        [InlineKeyboardButton(text="📊 /stats", callback_data="menu:stats"),
         InlineKeyboardButton(text="🎖 /achievements", callback_data="menu:ach")],
        [InlineKeyboardButton(text="📤 /upload", callback_data="menu:upload"),
         InlineKeyboardButton(text="🔔 /watch", callback_data="menu:watch")],
    ])

def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")]
    ])