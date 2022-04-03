import logging
import os
from typing import List
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards as kb
from main import add_image
from aiogram_media_group import MediaGroupFilter, media_group_handler
from database import Users, Events
from message_templates import artem_message
import settings

# Configure logging
logger = logging.getLogger('bot')

logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=settings.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# DB
users = Users(settings.DB_PATH)
events = Events(settings.DB_PATH)


class UploadPhotoForm(StatesGroup):
    photo = State()
    name = State()


@dp.message_handler(text='артем')
async def rofl(message: types.Message):
    await bot.send_message(chat_id=441246394, text=artem_message, parse_mode=types.ParseMode.HTML)
    await message.answer('Рофл отправил')


@dp.message_handler(commands=['start'])
async def process_hi6_command(message: types.Message):
    await message.answer("Привет",
                         reply_markup=kb.markup_request)
    users.add(message.from_user.id, message.from_user.first_name, message.from_user.last_name)


@dp.message_handler(text='Отправить фото')
async def get(message: types.Message, state: FSMContext):
    await state.update_data(msg_id=message.message_id)
    await UploadPhotoForm.photo.set()
    await message.answer(f'Загрузи фото, затем нажми <b>"Все"</b>.', reply_markup=kb.agree,
                         parse_mode=types.ParseMode.HTML)


@dp.message_handler(text='Все', state=UploadPhotoForm.photo)
async def End(message: types.Message, state: FSMContext):
    await message.answer('Дай имя файлу.')
    await UploadPhotoForm.name.set()


@dp.message_handler(state=UploadPhotoForm.name)
async def get(message: types.Message, state: FSMContext):
    data = (await state.get_data())['msg_id']

    try:
        await state.finish()
        filename = add_image(str(message.from_user.id), message.text.title())
        with open(filename, 'rb') as file:
            await message.answer_document(caption='Ваш документ',
                                          document=file,
                                          reply_markup=kb.markup_request)
        if message.from_user.id != 503760079:
            with open(filename, 'rb') as file:
                caption_user = f'id = {message.from_user.id}\n' \
                               f'first_name = {message.from_user["first_name"]}\n' \
                               f'user_name = {message.from_user["username"]}'
                await bot.send_document(-649937491, file, caption=caption_user)
                # print(message.from_user)
        os.remove(filename)
        events.add(message.from_user.id, filename)
    except Exception as e:
        await message.answer('Ошибка, пожалуйста следуй инструкции', reply_markup=kb.markup_request)
        logging.error(e)
    for msg_id in range(message.message_id, data - 1, -1):
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
    await message.answer(artem_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(lambda message: len(message.photo) == 0, state=UploadPhotoForm.photo)
async def process_photo_invalid(message: types.Message):
    return await message.reply("Фотография не найдена в сообщении!")


@dp.message_handler(content_types=['video'], state=UploadPhotoForm.photo)
async def process_photo_invalid(message: types.Message):
    return await message.reply("Фотография не найдена в сообщении!")


@dp.message_handler(MediaGroupFilter(), content_types=['photo'], state=UploadPhotoForm.photo)
@media_group_handler
async def album_handler(messages: List[types.Message]):
    for message in messages:
        await message.photo[-1].download(destination_file=f"{message.from_user.id}/file_{message.message_id}.jpg")


@dp.message_handler(content_types=['photo'], state=UploadPhotoForm.photo)
async def get_photo(message: types.Message):
    await message.photo[-1].download(destination_file=f"{message.from_user.id}/file_{message.message_id}.jpg")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
