import logging
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup
from fpdf import FPDF

import keyboards as kb
from main import add_image

API_TOKEN = '1597048067:AAGhPrQ6dDp1ZtGJ6H_f1MfJPyVw_myk1IM'

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
    await message.answer('Нажми все', reply_markup=kb.agree)


@dp.message_handler(text='Все', state=UploadPhotoForm.photo)
async def End(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Назвои файл', reply_markup=kb.markup_request)
    await UploadPhotoForm.name.set()


@dp.message_handler(state=UploadPhotoForm.name)
async def get(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer_document(caption='Ваш документ',
                                  document=open(add_image(str(message.from_user.id), message.text.title()), 'rb'))


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
    executor.start_polling(dp, skip_updates=True)
