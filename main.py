from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
import pickle

bot = Bot(token="TOKEN PLS")
dp = Dispatcher(bot)

tea_count = {}
user_tea = {}
user_purchases = {}

# Load data from pickle file if it exists
try:
    with open("tea_count.pkl", "rb") as f:
        tea_count = pickle.load(f)
except FileNotFoundError:
    pass

tea_shop = {"Черный": 0, "Зеленый": 5, "Улун": 10, "Фруктовый": 15}


@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    if user_id in tea_count:
        await message.reply(
            f"Добро пожаловать обратно, {user_name}! Вы можете использовать команду /tea чтобы выпить чашку своего "
            f"любимого сорта или /shop чтобы купить новый сорт.")
        return


    tea_count[user_id] = 0
    await message.reply(
        f"Добро пожаловать в наш чайный клуб, {user_name}! Вы можете выбрать свой первый сорт чая командой /choose.")


@dp.message_handler(commands=["shop"])
async def shop_handler(message: Message):
    shop_items = "\n".join([f"{tea} - {price} чашек" for tea, price in tea_shop.items()])
    await message.reply(f"Доступные сорты чая:\n{shop_items}")


@dp.message_handler(commands=["buy"])
async def buy_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    tea_choice = message.get_args()

    if not tea_choice:
        await message.reply("Пожалуйста, укажите название сорта чая.")
        return

    if tea_choice not in tea_shop:
        await message.reply(f"Извините, но у нас нет такого сорта как {tea_choice}.")
        return

    tea_price = tea_shop[tea_choice]

    if user_id not in tea_count or tea_count[user_id] < tea_price:
        await message.reply(f"Извините, но у вас недостаточно чашек для покупки {tea_choice}.")
        return

    if user_id not in user_purchases:
        user_purchases[user_id] = []

    user_purchases[user_id].append(tea_choice)

    tea_count[user_id] -= tea_price
    await message.reply(f"Вы купили {tea_choice} за {tea_price} чашек. У вас осталось {tea_count[user_id]} чашек.")
    print(f"{user_name} купил {tea_choice} чай за {tea_price} чашек чая. Осталось чашек чая: {tea_count[user_id]}")
    

@dp.message_handler(commands=["tea"])
async def tea_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    if user_id not in tea_count:
        tea_count[user_id] = 0

    if user_id not in user_tea or user_tea[user_id] not in tea_shop:
        await message.reply("Пожалуйста, выберите сорт чая командой /choose перед тем как выпить чашку.")
        return

    tea_choice = user_tea[user_id]

    if tea_choice == "Черный":
        tea_count[user_id] += 1
    elif tea_choice == "Зеленый":
        tea_count[user_id] += 5
    elif tea_choice == "Улун":
        tea_count[user_id] += 15
    elif tea_choice == "Фруктовый":
        tea_count[user_id] += 25

    await message.reply(f"Выпита чашка {tea_choice}. Всего чашек: {tea_count[user_id]}")
    print(f"{user_name} выпил чашку чая. У него на счету {tea_count[user_id]} чашек чая.")


@dp.message_handler(commands=["choose"])
async def choose_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    tea_choice = message.get_args()

    if not tea_choice:
        await message.reply("Пожалуйста, укажите название сорта чая.")
        return

    if tea_choice not in tea_shop:
        await message.reply(f"Извините, но у нас нет такого сорта как {tea_choice}.")
        return

    if user_id in user_purchases and tea_choice not in user_purchases[user_id]:
        await message.reply(f"Извините, но вы еще не купили {tea_choice}.")
        return

    if user_id not in user_purchases:
        user_purchases[user_id] = [tea_choice]

    user_tea[user_id] = tea_choice
    await message.reply(
        f"Вы выбрали {tea_choice}. Теперь каждый раз когда вы выпьете чашку этого сорта командой /tea вы получите соответствующее количество чашек.")

    # Save data to pickle file
    with open("tea_count.pkl", "wb") as f:
        pickle.dump(tea_count, f)


executor.start_polling(dp)
