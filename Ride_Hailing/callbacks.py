from aiogram.filters.callback_data import CallbackData
class Callback(CallbackData, prefix="my"):
    name: str
    id: int