from aiogram.utils.keyboard import InlineKeyboardBuilder

from data import SPECIALTIES


def specialties_keyboard():
    builder = InlineKeyboardBuilder()

    for key, specialty in SPECIALTIES.items():
        builder.button(
            text=specialty["name"],
            callback_data=f"specialty:{key}"
        )

    builder.adjust(1)

    return builder.as_markup()


def courses_keyboard():
    builder = InlineKeyboardBuilder()

    for course in range(1, 5):
        builder.button(
            text=f"📚 {course} курс",
            callback_data=f"course:{course}"
        )

    builder.adjust(2)

    return builder.as_markup()


def subjects_keyboard(specialty_key: str, course: int):
    builder = InlineKeyboardBuilder()

    subjects = SPECIALTIES[specialty_key]["courses"].get(course, [])

    for index, subject in enumerate(subjects):
        builder.button(
            text=subject,
            callback_data=f"subject:{index}"
        )

    builder.adjust(1)

    return builder.as_markup()


def main_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔎 Знайти завдання",
        callback_data="search"
    )

    builder.button(
        text="📚 Предмети",
        callback_data="subjects"
    )

    builder.button(
        text="📸 Розв'язати по фото",
        callback_data="photo"
    )

    builder.button(
        text="📅 Розклад",
        callback_data="schedule"
    )

    builder.button(
        text="⭐ Обране",
        callback_data="favorites"
    )

    builder.button(
        text="⚙️ Мій профіль",
        callback_data="profile"
    )

    builder.adjust(2)

    return builder.as_markup()
