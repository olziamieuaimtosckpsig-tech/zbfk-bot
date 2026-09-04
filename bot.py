import asyncio
import logging
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties

from data import SPECIALTIES
from keyboards import (
    specialties_keyboard,
    courses_keyboard,
    subjects_keyboard,
    main_keyboard,
)
from database import init_db, save_user, get_user


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

router = Router()


class SetupState(StatesGroup):
    specialty = State()
    course = State()
    subject = State()


class SearchState(StatesGroup):
    query = State()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):

    user = get_user(message.from_user.id)

    if user:
        specialty, course, subject = user

        await message.answer(
            "👋 С возвращением!\n\n"
            f"🎓 Специальность: {SPECIALTIES[specialty]['name']}\n"
            f"📚 Курс: {course}\n"
            f"📖 Предмет: {subject or 'не выбран'}\n\n"
            "Что будем делать?",
            reply_markup=main_keyboard()
        )

        return

    await state.set_state(SetupState.specialty)

    await message.answer(
        "👋 Привет!\n\n"
        "Я — помощник студента ЗБФК.\n\n"
        "Здесь можно будет искать задания, "
        "материалы и решения.\n\n"
        "🎓 Для начала выбери специальность:",
        reply_markup=specialties_keyboard()
    )


@router.callback_query(
    SetupState.specialty,
    F.data.startswith("specialty:")
)
async def select_specialty(
    callback: CallbackQuery,
    state: FSMContext
):

    specialty = callback.data.split(":")[1]

    await state.update_data(
        specialty=specialty
    )

    await state.set_state(SetupState.course)

    await callback.message.edit_text(
        "✅ Специальность выбрана!\n\n"
        "📚 Теперь выбери свой курс:",
        reply_markup=courses_keyboard()
    )

    await callback.answer()


@router.callback_query(
    SetupState.course,
    F.data.startswith("course:")
)
async def select_course(
    callback: CallbackQuery,
    state: FSMContext
):

    course = int(callback.data.split(":")[1])

    data = await state.get_data()

    specialty = data["specialty"]

    await state.update_data(
        course=course
    )

    await state.set_state(SetupState.subject)

    await callback.message.edit_text(
        "📖 Отлично!\n\n"
        "Теперь выбери предмет:",
        reply_markup=subjects_keyboard(
            specialty,
            course
        )
    )

    await callback.answer()


@router.callback_query(
    SetupState.subject,
    F.data.startswith("subject:")
)
async def select_subject(
    callback: CallbackQuery,
    state: FSMContext
):

    data = await state.get_data()

    specialty = data["specialty"]
    course = data["course"]

    index = int(callback.data.split(":")[1])

    subjects = SPECIALTIES[specialty]["courses"][course]

    subject = subjects[index]

    save_user(
        telegram_id=callback.from_user.id,
        specialty=specialty,
        course=course,
        subject=subject
    )

    await state.clear()

    await callback.message.edit_text(
        "🎉 Готово!\n\n"
        f"🎓 {SPECIALTIES[specialty]['name']}\n"
        f"📚 {course} курс\n"
        f"📖 {subject}\n\n"
        "Теперь можно искать задания 👇",
        reply_markup=main_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "search")
async def search_start(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(SearchState.query)

    await callback.message.answer(
        "🔎 Напиши, что нужно найти.\n\n"
        "Например:\n\n"
        "• задача 154\n"
        "• вариант 3\n"
        "• рассчитать балку\n"
        "• тема 5"
    )

    await callback.answer()


@router.message(SearchState.query)
async def search_handler(
    message: Message,
    state: FSMContext
):

    query = message.text

    user = get_user(message.from_user.id)

    if not user:

        await state.clear()

        await message.answer(
            "⚠️ Профиль ещё не настроен.\n\n"
            "Нажми /start и выбери специальность."
        )

        return

    specialty, course, subject = user

    await state.clear()

    await message.answer(
        "🔎 Ищу задание...\n\n"
        f"🎓 {SPECIALTIES[specialty]['name']}\n"
        f"📚 {course} курс\n"
        f"📖 {subject}\n\n"
        f"🔍 Запрос: {query}"
    )

    await message.answer(
        "📚 База заданий пока находится в разработке.\n\n"
        "Следующим этапом подключим реальные "
        "задания и материалы колледжа."
    )


@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    user = get_user(callback.from_user.id)

    if not user:

        await callback.message.answer(
            "⚠️ Профиль ещё не настроен.\n\n"
            "Используй /start."
        )

        await callback.answer()
        return

    specialty, course, subject = user

    await callback.message.answer(
        "👤 Твой профиль\n\n"
        f"🎓 Специальность: "
        f"{SPECIALTIES[specialty]['name']}\n"
        f"📚 Курс: {course}\n"
        f"📖 Предмет: {subject}"
    )

    await callback.answer()


@router.callback_query(F.data == "subjects")
async def subjects(callback: CallbackQuery):

    user = get_user(callback.from_user.id)

    if not user:

        await callback.message.answer(
            "⚠️ Сначала настрой профиль через /start."
        )

        await callback.answer()
        return

    specialty, course, _ = user

    await callback.message.answer(
        "📚 Предметы твоего курса:",
        reply_markup=subjects_keyboard(
            specialty,
            course
        )
    )

    await callback.answer()


@router.callback_query(F.data == "photo")
async def photo(callback: CallbackQuery):

    await callback.message.answer(
        "📸 Функция решения по фотографии будет "
        "добавлена следующим этапом.\n\n"
        "Ты сможешь отправить фото задания, "
        "а бот попробует распознать его."
    )

    await callback.answer()


@router.callback_query(F.data == "schedule")
async def schedule(callback: CallbackQuery):

    await callback.message.answer(
        "📅 Раздел расписания пока в разработке.\n\n"
        "Позже подключим расписание ЗБФК."
    )

    await callback.answer()


@router.callback_query(F.data == "favorites")
async def favorites(callback: CallbackQuery):

    await callback.message.answer(
        "⭐ Избранное пока пустое.\n\n"
        "Эту функцию подключим вместе с базой заданий."
    )

    await callback.answer()


async def main():

    logging.basicConfig(
        level=logging.INFO
    )

    if not TOKEN:
        raise RuntimeError(
            "Не найден BOT_TOKEN"
        )

    init_db()

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    dp.include_router(router)

    print("🤖 ЗБФК-бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
