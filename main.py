#telegram api key
# 6128302810:AAFBv5UNfWP0qTPD4ZuvASDN_CujOru-C_I

import sqlite3
from aiogram import Bot,Dispatcher, executor,types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging
import json
import requests
import re
from KEY_ALL import TG_key
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext # указываем что это из дисп состояний
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAdmin(StatesGroup):
    ip = State()
    


connect = sqlite3.connect('data_list1.db')
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users(
id_user VARCHAR (50))
''')
connect.cursor()


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TG_key)
dp = Dispatcher(bot, storage=MemoryStorage())

b1 = KeyboardButton("/start")
b2 = KeyboardButton('/statistics')
b3 = KeyboardButton('/ip')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1).add(b2).add(b3)

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    user_id = message.from_user.id
    checking = cursor.execute("SELECT * FROM users WHERE id_user=?", (user_id,)).fetchone()
    if len(str(checking)) == 0:
        cursor.execute("INSERT INTO users VALUES(?) ", [user_id])
        connect.commit()
        await bot.send_message(user_id, 'Привет, пользователь с номером {}!'.format(user_id), reply_markup=kb_client)
    else:
        await bot.send_message(user_id, 'Пользователь {}, кажется, мы уже общались!'.format(user_id),reply_markup=kb_client)
   

@dp.message_handler(commands=['statistics'])
async def command_start(message: types.Message):
    user_id = message.from_user.id
    all = cursor.execute('SELECT * FROM users').fetchall()
    lens = len(all)
    await bot.send_message(user_id, 'Я уже пообщался с {} пользователями!'.format(str(lens)),reply_markup= kb_client)


@dp.message_handler(commands='ip',state=None)
async def check_ip(message: types.Message, state=FSMContext):
    await message.reply('Введите IP, за которым следим')
    await FSMAdmin.ip.set()



@dp.message_handler(state=FSMAdmin.ip)
async def loan_ip(message: types.Message,state=FSMContext):
    async with state.proxy() as data:
        data['ip'] = message.text
        if (re.fullmatch(r"^[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}", str(data['ip'])) is not None) != False :
            try:
                await bot.send_message(message.from_user.id, "IP")
                data1 = requests.get("https://ipinfo.io/{}/geo".format(data["ip"]),\
                                params={"city": message.text.upper(),"region": message.text.upper(),\
                                "country": message.text.upper(),"loc":message.text.upper()}).text
                data1 = json.loads(data1)
                await bot.send_message(message.from_user.id,"Данные о вашем местонахождении: \
                                \nГород : {}\nРегион: {}\nСтрана: {}\nГеографические координаты: {}".\
                                format(data1['city'],data1["region"],data1["country"],data1["loc"]))
            except:
                await bot.send_message(message.from_user.id,"Кажется это все-таки не ip...")
        else:
            await bot.send_message(message.from_user.id, "Кажется, это не IP")
    



#запустить бот
if __name__ == "__main__" :
    executor.start_polling(dp,skip_updates=True)

    