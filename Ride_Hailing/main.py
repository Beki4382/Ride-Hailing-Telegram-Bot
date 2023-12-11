import asyncio
from datetime import datetime
import json
import logging
import os
import random
import sys
from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from flask import Flask, abort
from phonenumbers import PhoneNumber

from aiohttp import request, web

from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


TOKEN = ''

router = Router()





class RideBookingStates(StatesGroup):
    REQUEST_START = State()
    REQUEST_DESTINATION = State()

# Load user data from file (as previously defined)

# Define a dictionary to store ongoing ride requests

ongoing_rides = {}



class RatingStates(StatesGroup):
    RATING = State()
    REVIEW = State()

try:
    with open('user_data.json', 'r') as file:
        users = json.load(file)
except FileNotFoundError:
    users = {}

try:
    with open('ongoing_rides.json', 'r') as file:
        ongoing_rides = json.load(file)
except FileNotFoundError:
    ongoing_rides = {}

drivers = set()  # Set to store driver user_ids

# New dictionaries to store ratings, reviews, and ride history
user_ratings = {}
user_reviews = {}
ride_history = {}

def save_users_to_file():
    with open('user_data.json', 'w') as file:
        json.dump(users, file, indent=2)

def save_ongoing_rides_to_file():
    with open('ongoing_rides.json', 'w') as file:
        json.dump(ongoing_rides, file, indent=2)

# Save ratings, reviews, and ride history to file
def save_ratings_reviews_history_to_file():
    with open('ratings_reviews_history.json', 'w') as file:
        json.dump({
            'user_ratings': user_ratings,
            'user_reviews': user_reviews,
            'ride_history': ride_history
        }, file, indent=2)



# Save ongoing ride requests to file

def save_ongoing_rides_to_file():
    with open('ongoing_rides.json', 'w') as file:
        json.dump(ongoing_rides, file, indent=2)
# States
class RegistrationStates(StatesGroup):
    START = State()
    NAME = State()
    PHONE = State()
    ROLE = State()
    PROFILE_EDIT = State()
    LOCATION = State()
    DESTINATION = State()

# Load user data from file
try:
    with open('user_data.json', 'r') as file:
        users = json.load(file)
except FileNotFoundError:
    users = {}

# Save user data to file
def save_users_to_file():
    with open('user_data.json', 'w') as file:
        json.dump(users, file, indent=2)

# Set up Flask app
app = Flask(__name__)

# Webhook enrouteroint
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_data)
        router.process_update(update)
        return ''
    else:
        abort(403)



async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")



@router.message(CommandStart())
async def cmd_start(message: Message,  state: FSMContext):
    user_id = str(message.from_user.id)
    print( await state.get_data())
    if user_id in users:
        await state.set_state(RegistrationStates.PROFILE_EDIT)
        await message.reply("You have already registered.")
    else:
        users[user_id] = {}
        save_users_to_file(users=users)

        await state.set_state(RegistrationStates.NAME)
        await message.reply("Welcome! Let's start the registration process. What's your full name?")

# Registration process
@router.message(RegistrationStates.NAME)
async def process_name(message: Message, state: FSMContext):
    user_id = str(str(message.from_user.id))
    users[user_id]['name'] = message.text
    save_users_to_file(users=users)
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.PHONE)
    await message.answer("Please share your contact",reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Share Contact", request_contact=True),
                    
                    ]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            ),)
@router.message(RegistrationStates.PHONE)
async def process_phone(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    users[user_id]['phone'] = message.contact.phone_number
    save_users_to_file(users=users)
    await state.update_data(phone=message.contact.phone_number)

    await state.set_state(RegistrationStates.ROLE)
    await message.reply("Got it! Are you a driver or a passenger?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Driver"), KeyboardButton(text="Passenger")]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))

# Save user role
@router.message(lambda message: message.text.lower() in ["driver", "passenger"], RegistrationStates.ROLE)
async def process_role(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    users[user_id]['role'] = message.text.lower()
    save_users_to_file(users=users)
    await state.update_data(role=message.text)
    
    data = await state.get_data()
    print(data)

    await state.set_state(RegistrationStates.PROFILE_EDIT)
    await message.reply("Registration complete! You can now edit your profile.")


# Command to start the profile editing process
@router.message(Command('edit_profile'))
async def cmd_edit_profile(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if str(user_id) not in users:
        await message.reply("Please complete the registration process first with /start.")
        return

    await state.set_state(RegistrationStates.NAME)
    await message.reply("Please enter your new full name.")



# Implement ride booking logic

@router.message(Command('request_ride'))
async def cmd_request_ride(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if str(user_id) not in users:
        await message.reply("Please complete the registration process first with /start.")
        return

    await state.set_state(RideBookingStates.REQUEST_START)
    await message.reply("Where would you like to start your ride?")

@router.message(RideBookingStates.REQUEST_START)
async def process_ride_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    ongoing_rides[user_id] = {'start_location': message.text}
    save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)

    await state.set_state(RideBookingStates.REQUEST_DESTINATION)
    await message.reply("Great! Now, please provide your destination.")

@router.message(RideBookingStates.REQUEST_DESTINATION)
async def process_ride_destination(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    ongoing_rides[user_id]['destination'] = message.text
    save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)

    # Notify all drivers about the ride request (simplified for demo purposes)
    await bot.send_message(user_id, "Searching for nearby drivers...")
    await state.set_state(RatingStates.RATING)
    for driver_user_id in users:
        if users[driver_user_id]['role'] == 'driver':
            await bot.send_message(driver_user_id, f"New ride request from user {user_id}. Start: {ongoing_rides[user_id]['start_location']}, Destination: {ongoing_rides[user_id]['destination']}.")
    
    await message.reply("Your ride request has been sent to nearby drivers. Please wait for a response.")

# Implement driver matching logic

# @router.message(Command('accept_ride'))
# async def cmd_accept_ride(message: Message, state: FSMContext):
#     driver_id = str(message.from_user.id)
#     if str(driver_id) not in users or users[str(driver_id)]['role'] != 'driver':
#         await message.reply("Only registered drivers can accept rides.")
#         return

#     # Simulate a simple driver matching algorithm (simplified for demo purposes)
#     user_ids = [user_id for user_id in ongoing_rides if 'driver' not in ongoing_rides[user_id]]
#     if not user_ids:
#         await message.reply("No available ride requests at the moment.")
#         return

#     # Simulate a simple driver matching algorithm (simplified for demo purposes)
#     user_ids = [user_id for user_id in ongoing_rides if 'driver' not in ongoing_rides[user_id]]
#     if not user_ids:
#         await message.reply("No available ride requests at the moment.")
#         return

#     # Create a list of InlineKeyboardButton for each ride request
#     buttons = [InlineKeyboardButton(f"Ride request from {user_id}", callback_data=user_id) for user_id in user_ids]
#     keyboard = InlineKeyboardMarkup(row_width=1)
#     keyboard.add(*buttons)

#     # Send the list of ride requests as a reply markup
#     await bot.send_message(driver_id, "Here are the available ride requests:", reply_markup=keyboard)
#     save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)
    
#     ride_info = ongoing_rides[user_id].copy()  # Copy the ride info
#     ride_info['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add the current date and time
#     if user_id not in ride_history:
#         ride_history[user_id] = []  # Initialize the user's ride history if it doesn't exist
#     ride_history[user_id].append(ride_info)  # Add the ride info to the user's ride history

# # Update ride history for driver
#     if str(driver_id) not in ride_history:
#         ride_history[driver_id] = []  # Initialize the driver's ride history if it doesn't exist
#     ride_history[driver_id].append(ride_info)  # Add the ride info to the driver's ride history

#     save_ratings_reviews_history_to_file(ride_history=ride_history)  # Save the updated ride history to file

#     await bot.send_message(driver_id, f"You have accepted the ride request from user {user_id}. Start: {ongoing_rides[user_id]['start_location']}, Destination: {ongoing_rides[user_id]['destination']}.")
#     await bot.send_message(user_id, f"Your ride request has been accepted by driver {driver_id}. Driver's details will be provided shortly.")
    
#     await state.set_state(RatingStates.RATING)
#     await bot.send_message(user_id, "How would you rate your ride? (1-5)")
#     await bot.send_message(driver_id, "How would you rate your ride? (1-5)")






@router.message(Command('accept_ride'))
async def cmd_accept_ride(message: Message, state: FSMContext):
    driver_id = str(message.from_user.id)
    if str(driver_id) not in users or users[str(driver_id)]['role'] != 'driver':
        await message.reply("Only registered drivers can accept rides.")
        return

    # Get all user_ids where the 'driver' key is not present in ongoing_rides
    user_ids = [user_id for user_id in ongoing_rides if 'driver' not in ongoing_rides[user_id]]
    if not user_ids:
        await message.reply("No available ride requests at the moment.")
        return

    # Create a list of InlineKeyboardButton for each ride request
    lst = []
    for user_id in user_ids:
        button = InlineKeyboardButton(text=f"Ride request from {user_id}" ,callback_data=user_id ) 
        print(button, "here are the buttons")
        lst.append(button)
    
    print(lst)

    # Send the list of ride requests as a reply markup
    await bot.send_message(driver_id, "Here are the available ride requests:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[lst]))



@router.callback_query(lambda c: True)
async def process_callback(callback_query: CallbackQuery , state: FSMContext):
    driver_id = str(callback_query.from_user.id)
    user_id = callback_query.data  # This is the user_id you set as callback_data in the InlineKeyboardButton

    # Now you can process the ride request acceptance
    ongoing_rides[user_id]['driver'] = driver_id
    save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)
    
    ride_info = ongoing_rides[user_id].copy()  # Copy the ride info
    ride_info['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add the current date and time
    if user_id not in ride_history:
        ride_history[user_id] = []  # Initialize the user's ride history if it doesn't exist
    ride_history[user_id].append(ride_info)  # Add the ride info to the user's ride history

    # Update ride history for driver
    if str(driver_id) not in ride_history:
        ride_history[driver_id] = []  # Initialize the driver's ride history if it doesn't exist
    ride_history[driver_id].append(ride_info)  # Add the ride info to the driver's ride history

    save_ratings_reviews_history_to_file(ride_history=ride_history)  # Save the updated ride history to file

    await bot.send_message(driver_id, f"You have accepted the ride request from user {user_id}. Start: {ongoing_rides[user_id]['start_location']}, Destination: {ongoing_rides[user_id]['destination']}.")
    await bot.send_message(user_id, f"Your ride request has been accepted by driver {driver_id}. Driver's details will be provided shortly.")
    
    await state.set_state(RatingStates.RATING)
    await bot.send_message(user_id, "How would you rate your ride? (1-5)")
    await bot.send_message(driver_id, "How would you rate your ride? (1-5)")

    # Don't forget to answer the callback query or the user will see a loading spinner forever
    await bot.answer_callback_query(callback_query.id)        
            
            
@router.message(RatingStates.RATING)
async def process_rating(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    try:
        rating = int(message.text)
        if 1 <= rating <= 5:
            user_ratings[user_id] = rating
            ride_history[user_id][-1]['rating'] = rating  # Add rating to the last ride in the ride history

            save_ratings_reviews_history_to_file(ride_history=ride_history)
            await state.set_state(RatingStates.REVIEW)
            await message.reply("Thank you! Please provide a review for your ride.")
        else:
            await message.reply("Please enter a rating between 1 and 5.")
    except ValueError:
        await message.reply("Please enter a valid number between 1 and 5.")
        

@router.message(RatingStates.REVIEW)
async def process_review(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    review = message.text
    user_reviews[user_id] = review
    ride_history[user_id][-1]['review'] = review  # Add review to the last ride in the ride history
    print(ride_history[user_id], "hereeeeeeee")  # Add this line
    save_ratings_reviews_history_to_file(ride_history=ride_history)
    await state.set_state(RegistrationStates.START)

    await message.reply("Thank you for your feedback!")


# Handling History
@router.message(Command('view_ride_history'))
async def cmd_view_ride_history(message: Message):
    user_id = str(message.from_user.id)
    if str(user_id) not in users or (users[user_id]['role'] != 'driver' and users[user_id]['role'] != 'passenger'):
        await message.reply("Only registered drivers or passengers can use this command.")
        return

    if str(user_id) not in ride_history:
        await message.reply("No ride history available.")
        return

    history_message = "Your ride history:\n"
    for ride_info in ride_history[user_id]:
        history_message += f"- {ride_info['start_location']} to {ride_info['destination']}\n"
        history_message += f"  Date: {ride_info['date']}\n"
        if 'rating' in ride_info:
            history_message += f"  Rating: {ride_info['rating']}\n"
            history_message += f"  Review: {ride_info['review']}\n"
        history_message += "\n"

    await message.reply(history_message)




async def main() -> None:
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()