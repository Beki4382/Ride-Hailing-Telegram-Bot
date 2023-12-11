# import sqlite3
# from aiogram import types
# from aiogram.types import (
#     KeyboardButton,
#     Message,
#     ReplyKeyboardMarkup,
#     InlineKeyboardButton,
#     ReplyKeyboardRemove,
#     InlineKeyboardMarkup
# )
# from aiogram.utils.markdown import hbold
# from aiogram.fsm.context import FSMContext

# from callbacks import Callback


# async def process_driver_role(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
#     # await query.message.delete()
#     await state.update_data(role="driver")
#     await query.message.answer(f"✅ Successfully registered.")

#     # Store user data in SQLite
#     user_data = await state.get_data()
#     conn = sqlite3.connect('ride_healing/users.db')
#     cursor = conn.cursor()

#     user_id = query.message.chat.id
#     username = user_data.get('fullname')
#     phone = user_data.get('phone')
#     role = "driver"
#     date = user_data.get('date')

#     cursor.execute('''
#         INSERT INTO users (
#             user_id, username, state, fullname, phone, role,
#             history, registration_date, rating, completed_rides
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         user_id, username, 'state1',
#         username, phone, role,
#         "", date,
#         0, "[]"
#     ))
#     conn.commit()
#     conn.close()
#     await query.message.delete()
#     menu = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='🚘 Book Ride', callback_data=Callback(name="ride", id="4").pack()),
#     InlineKeyboardButton(text='🔁 Driver Matching', callback_data=Callback(name="match", id="5").pack())],
#     [InlineKeyboardButton(text='⭐️ Rate Driver', callback_data=Callback(name="rate", id="6").pack()),
#     InlineKeyboardButton(text='🧾 History', callback_data=Callback(name="history", id="7").pack())],
#     [InlineKeyboardButton(text='⚙️ Profile', callback_data=Callback(name="profile", id="8").pack())],], )
#     await query.message.answer(f"{hbold("Welcome to Ride Healing Bot")}!\n\nSteer your ride! Where would you like to go?\nSelect from features ..  ", reply_markup=menu)
 