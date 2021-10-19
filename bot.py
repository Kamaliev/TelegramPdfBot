import logging
import os
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards as kb
from config import Token
from main import add_image

API_TOKEN = Token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UploadPhotoForm(StatesGroup):
    photo = State()
    name = State()


@dp.message_handler(commands=['start'])
async def process_hi6_command(message: types.Message):
    await message.answer("Привет",
                         reply_markup=kb.markup_request)


@dp.message_handler(text='Отправить фото')
async def get(message: types.Message):
    await UploadPhotoForm.photo.set()
    await message.answer('Загрузи фото, затем нажми "Все".', reply_markup=kb.agree)


@dp.message_handler(text='Все', state=UploadPhotoForm.photo)
async def End(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Дай имя файлу.')
    await UploadPhotoForm.name.set()


@dp.message_handler(state=UploadPhotoForm.name)
async def get(message: types.Message, state: FSMContext):
    await state.finish()
    filename = add_image(str(message.from_user.id), message.text.title())
    with open(filename, 'rb') as file:
        await message.answer_document(caption='Ваш документ',
                                      document=file,
                                      reply_markup=kb.markup_request)
    with open(filename, 'rb') as file:
        caption_user = f'id = {message.from_user.id}\n' \
                       f'first_name = {message.from_user["first_name"]}\n' \
                       f'user_name = {message.from_user["username"]}'
        await bot.send_document(-649937491, file, caption=caption_user)
        # print(message.from_user)

    os.remove(filename)


@dp.message_handler(lambda message: len(message.photo) == 0, state=UploadPhotoForm.photo)
async def process_photo_invalid(message: types.Message):
    return await message.reply("Фотография не найдена в сообщении!")


@dp.message_handler(content_types=['photo'], state=UploadPhotoForm.photo)
async def get_photo(message: types.Message, state: FSMContext):
    file_info = await bot.get_file(message.photo[-1].file_id)
    await message.photo[-1].download(f"{message.from_user.id}/{file_info.file_path.split('photos/')[1]}")
    await state.finish()
    await UploadPhotoForm.photo.set()


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except:
            pass
        time.sleep(5)
