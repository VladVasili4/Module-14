from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging

from crud_functions import *


api = '123k'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


in_kb = InlineKeyboardMarkup()
in_button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
in_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
in_kb.add(in_button1)
in_kb.add(in_button2)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.add(button1)
kb.insert(button2)
kb.add(button3)

by_kb = InlineKeyboardMarkup(inline_keyboard=[
    [KeyboardButton(text='Product1',callback_data='product_buying')],
    [KeyboardButton(text='Product2',callback_data='product_buying')],
    [KeyboardButton(text='Product3',callback_data='product_buying')],
    [KeyboardButton(text='Product4',callback_data='product_buying')]], resize_keyboard=True)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


get_all_products()

@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for number in range(1,5):
        with open(f'Tovary/{number}.jpg', 'rb') as img_number:
            await message.answer_photo(img_number, f'Название: Product{number} | Описание: описание {number} '
                                       f'| Цена: {number*100}')
        await message.answer("Выберите продукт для покупки:", reply_markup=by_kb)

@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=in_kb)

@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer('мужчинам: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5; \n '
                              'женщинам: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    # await call.answer         # чтобы инлайн-кнопка после выполнения команды становилась кликабельна.
                                # Hо у меня и без этой команды она кликабельна ?????? !!!!!!)

@dp.message_handler(text=['Информация'])
async def inform(message):
    await message.answer('Это бот для рассчета калорий, необходимых ежедневно человеку, '
                         'в зависимости от параметров человека')

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(user_age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(user_growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(user_weight=message.text)
    data = await state.get_data(['user_age', 'user_growth', 'user_weight'])
    count_calories = (10.0 * float(data['user_weight']) + 6.25 * float(data['user_growth'])
                      - 5.0 * float(data['user_age']) + 5)
    await message.answer(f'Ваша норма калорий : {count_calories} ')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
