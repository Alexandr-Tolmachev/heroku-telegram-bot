import os

from aiohttp import ClientSession
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from film_getters import Wiki, Kinopoisk


bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher(bot)

wiki_getter = Wiki()
kinopoisk_getter = Kinopoisk()


@dp.message_handler(commands=['help', 'start'])
async def _help(message: types.Message) -> None:
    await message.reply("Это бот для поиска фильмов. \nВведите название своего фильма: \n")


@dp.message_handler()
async def _get_film_info(message: types.Message) -> None:
    async with ClientSession() as session:
        wiki_dict = await wiki_getter.get_film_info(session, message.text)
        kinopoisk_dict = await kinopoisk_getter.get_film_info(session, message.text)
        caption = '{}\n\nСсылка для просмотра: {}\n'.format(wiki_dict['text_info'], kinopoisk_dict['film_link'])

        await message.reply_photo(photo=wiki_dict['picture'], caption=caption)

if __name__ == '__main__':
    executor.start_polling(dp)
