import sqlite3
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from aiogram import types

async def process_user_profile(query: types.CallbackQuery, state, hbold, MyCallback):
    user_data = await state.get_data()
    user_id = query.message.chat.id
    print("User ID:", user_id)

    # Retrieve user data from SQLite
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user_profile = cursor.fetchone()
    print("User profile:", user_profile)

    conn.close()
    if user_profile:
        # Extract information from the database
        _, _, fullname, _, _, phone, role, _, registration_date, _, _ = user_profile

        # Format the text with retrieved information
        text = f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        text += f"{hbold('User Profile')}\n"
        text += f"Full Name: {fullname}\n"
        text += f"Phone Number: {phone}\n"
        text += f"Role: {role}\n"
        text += f"Registration Date: {registration_date}\n\n"
        text += f"@ride_hailing\nㅤ"
    else:
        text = "User profile not found."

    user_profile_photos = await query.message.from_user.get_profile_photos(limit=1)
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔄 Home', callback_data=MyCallback(name="home", id="3").pack()),
         InlineKeyboardButton(text='📝 Edit Profile ', callback_data=MyCallback(name="profile", id="8").pack())],
        [InlineKeyboardButton(text='📈 See your History ', callback_data=MyCallback(name="history", id="7").pack())], ])

    if user_profile_photos:
        match = re.search(r"file_id='(.*?)'", str(user_profile_photos))
        if match:
            photo_file_id = match.group(1)
            print("File ID:", photo_file_id)
            await query.message.answer_photo(photo=photo_file_id, caption=text, reply_markup=menu)
        else:
            print("File ID not found.")
            await query.message.answer(text, reply_markup=menu)