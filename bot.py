import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен жана администратор ID
API_TOKEN = '8273226401:AAFJgyvNaskohUZTpxY64jy5np-7q4eH5HM'
ADMIN_ID = 5148336517

# Тилдер
LANGUAGES = {
    'kg': 'кыргызча',
    'ru': 'русский',
    'en': 'english'
}

# Колдонуучунун тилин сактоо үчүн база
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (user_id INTEGER PRIMARY KEY, language TEXT DEFAULT 'kg')''')
    conn.commit()
    conn.close()

def add_user(user_id, language='kg'):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)', 
                   (user_id, language))
    conn.commit()
    conn.close()

def update_user_language(user_id, language):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'kg'

def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

# Текстерди тилдер боюнча
TEXTS = {
    'kg': {
        'start': "Салам, {name}! 👋\n\nБул **ОшМУ Студенттик кеңешинин** расмий боту. Төмөнкү бөлүмдөрдүн бирин тандаңыз:",
        'menu': "Негизги меню:",
        'feedback': "Сураныч, сунушуңузду же пикириңизди жазып жөнөтүңүз. 👇",
        'feedback_received': "Рахмат! Сиздин билдирүүңүз кабыл алынды жана каралат. ✅",
        'feedback_sent': "📩 **ЖАҢЫ ПИКИР КЕЛДИ:**\n\n\"{text}\"\n\n👤 Кимден: {name} (@{username})\n🆔 ID: {user_id}",
        'links': "Керектүү шилтемени тандаңыз: 👇",
        'faq': "❓ **Көп берилүүчү суроолор:**\n\n1️⃣ **Контрактты кайдан төлөйм?**\n— MyEDU платформасынан жеке эсеп алып аны Finca BANKтын терминалдары аркылуу төлөй аласыз.\n\n2️⃣ **2025-2026-окуу жылына контракт баалары кандай?**\n— Контракт баалары боюнча толук прейскурантты бул жерден көрө аласыз: [Контракт бааларын көрүү (PDF)](https://www.oshsu.kg/storage/uploads/files/21752775966preyskursant_zhany_2025-2026_okuu_zhylyna.pdf)",
        'about': """🏢 **Студенттик кеңеш жөнүндө**

**Студенттик кеңеш** — бул жогорку окуу жайдагы студенттердин өз алдынча уюштурулган органы. Негизги максаты — студенттердин кызыкчылыгын коргоо, иш-чараларды уюштуруу жана администрация менен студенттерди байланыштыруучу көпүрө болуу.

✅ **Негизги функциялары:**
🔹 Окуу жайдагы маселелерди жетекчиликке жеткирүү;
🔹 Маданий, спорттук, социалдык иш-чараларды уюштуруу;
🔹 Жаңы студенттерге жардам берүү (адаптация, багыт берүү);
🔹 Стипендия, жатакана маселелеринде колдоо көрсөтүү;
🔹 Коомдук иштерге студенттерди тартуу.

📜 **Тарыхы:**
Окуу жайдагы жаштар уюмунун тарыхы 1951-жылы Ош пединституту түзүлгөндөн тартып башталат. 1992-жылы комсомол комитетинин ордуна **студенттик сенат** түзүлгөн. Ал эми 2000-жылдын 10-декабрындагы КР Президентинин указына ылайык, студенттик сенат **жаштар комитети** болуп кайрадан түзүлгөн.

🚀 Азыркы учурда жаштар комитети студенттер менен жетекчилерди тыгыз байланыштырган миссияны аркалап, студенттердин кадыр-барктуу уюму катары иш алып барууда.""",
        'broadcast_success': "Билдирүү {count} колдонуучуга жөнөтүлдү! ✅",
        'broadcast_empty': "Сураныч, текстти кошо жазыңыз. Мисалы: `/send Салам студенттер!`",
        'language_changed': "Тил ийгиликтүү өзгөртүлдү! ✅",
        'choose_language': "Сураныч, тилди тандаңыз:",
        'back': "Артка",
        'change_language': "🌐 Тилди өзгөртүү"
    },
    'ru': {
        'start': "Привет, {name}! 👋\n\nЭто официальный бот **Студенческого совета ОшГУ**. Выберите один из разделов ниже:",
        'menu': "Главное меню:",
        'feedback': "Пожалуйста, напишите и отправьте ваше предложение или отзыв. 👇",
        'feedback_received': "Спасибо! Ваше сообщение получено и будет рассмотрено. ✅",
        'feedback_sent': "📩 **НОВЫЙ ОТЗЫВ:**\n\n\"{text}\"\n\n👤 От: {name} (@{username})\n🆔 ID: {user_id}",
        'links': "Выберите нужную ссылку: 👇",
        'faq': "❓ **Часто задаваемые вопросы:**\n\n1️⃣ **Где оплатить контракт?**\n— Вы можете получить личный счет на платформе MyEDU и оплатить его через терминалы Finca BANK.\n\n2️⃣ **Какие цены на контракт на 2025-2026 учебный год?**\n— Полный прайс-лист по ценам на контракт можно посмотреть здесь: [Посмотреть цены на контракт (PDF)](https://www.oshsu.kg/storage/uploads/files/21752775966preyskursant_zhany_2025-2026_okuu_zhylyna.pdf)",
        'about': """🏢 **О Студенческом совете**

**Студенческий совет** — это самостоятельный орган студентов высшего учебного заведения. Основная цель — защита интересов студентов, организация мероприятий и служить связующим мостом между администрацией и студентами.

✅ **Основные функции:**
🔹 Доведение проблем в вузе до руководства;
🔹 Организация культурных, спортивных, социальных мероприятий;
🔹 Помощь новым студентам (адаптация, ориентация);
🔹 Поддержка по вопросам стипендии, общежития;
🔹 Привлечение студентов к общественной деятельности.

📜 **История:**
История молодежной организации в вузе начинается с 1951 года, когда был основан Ошский пединститут. В 1992 году вместо комсомольского комитета был создан **студенческий сенат**. А согласно указу Президента КР от 10 декабря 2000 года, студенческий сенат был реорганизован в **комитет молодежи**.

🚀 В настоящее время комитет молодежи выполняет миссию по тесному взаимодействию студентов и руководства, работая как уважаемая организация студентов.""",
        'broadcast_success': "Сообщение отправлено {count} пользователям! ✅",
        'broadcast_empty': "Пожалуйста, добавьте текст. Например: `/send Привет студенты!`",
        'language_changed': "Язык успешно изменен! ✅",
        'choose_language': "Пожалуйста, выберите язык:",
        'back': "Назад",
        'change_language': "🌐 Сменить язык"
    },
    'en': {
        'start': "Hello, {name}! 👋\n\nThis is the official bot of **OshSU Student Council**. Please choose one of the sections below:",
        'menu': "Main menu:",
        'feedback': "Please write and send your suggestion or feedback. 👇",
        'feedback_received': "Thank you! Your message has been received and will be reviewed. ✅",
        'feedback_sent': "📩 **NEW FEEDBACK:**\n\n\"{text}\"\n\n👤 From: {name} (@{username})\n🆔 ID: {user_id}",
        'links': "Choose the needed link: 👇",
        'faq': "❓ **Frequently Asked Questions:**\n\n1️⃣ **Where to pay the contract?**\n— You can get a personal account on the MyEDU platform and pay it through Finca BANK terminals.\n\n2️⃣ **What are the contract prices for 2025-2026 academic year?**\n— You can view the full price list for contract prices here: [View contract prices (PDF)](https://www.oshsu.kg/storage/uploads/files/21752775966preyskursant_zhany_2025-2026_okuu_zhylyna.pdf)",
        'about': """🏢 **About Student Council**

**Student Council** is an independent body of students in a higher education institution. The main goal is to protect students' interests, organize events, and serve as a bridge between administration and students.

✅ **Main functions:**
🔹 Conveying university issues to the leadership;
🔹 Organizing cultural, sports, social events;
🔹 Helping new students (adaptation, orientation);
🔹 Supporting scholarship, dormitory issues;
🔹 Engaging students in social activities.

📜 **History:**
The history of youth organization in the university starts from 1951 when Osh Pedagogical Institute was founded. In 1992, instead of the Komsomol committee, **Student Senate** was created. And according to the decree of the President of the Kyrgyz Republic dated December 10, 2000, the student senate was reorganized into **Youth Committee**.

🚀 Currently, the Youth Committee carries out the mission of close interaction between students and leadership, working as a respected student organization.""",
        'broadcast_success': "Message sent to {count} users! ✅",
        'broadcast_empty': "Please add text. For example: `/send Hello students!`",
        'language_changed': "Language successfully changed! ✅",
        'choose_language': "Please choose language:",
        'back': "Back",
        'change_language': "🌐 Change language"
    }
}

# Кнопкалардын текстери
BUTTONS = {
    'kg': {
        'feedback': "✍️ Сунуш же пикир калтыруу",
        'faq': "❓ Көп берилүүчү суроолор (FAQ)",
        'links': "🔗 Пайдалуу шилтемелер",
        'about': "ℹ️ Биз жөнүндө",
        'website': "🌐 ОшМУ расмий сайт",
        'members': "🌐 ОшМУ студенттик кеңешинин курамы",
        'myedu': "📚 MyEDU",
        'instagram': "📸 Инстаграм баракчабыз"
    },
    'ru': {
        'feedback': "✍️ Оставить предложение или отзыв",
        'faq': "❓ Часто задаваемые вопросы (FAQ)",
        'links': "🔗 Полезные ссылки",
        'about': "ℹ️ О нас",
        'website': "🌐 Официальный сайт ОшГУ",
        'members': "🌐 Состав студсовета ОшГУ",
        'myedu': "📚 MyEDU",
        'instagram': "📸 Наша страница в Instagram"
    },
    'en': {
        'feedback': "✍️ Leave suggestion or feedback",
        'faq': "❓ Frequently Asked Questions (FAQ)",
        'links': "🔗 Useful links",
        'about': "ℹ️ About us",
        'website': "🌐 OshSU official website",
        'members': "🌐 OshSU Student Council members",
        'myedu': "📚 MyEDU",
        'instagram': "📸 Our Instagram page"
    }
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

init_db()

# Тил тандатуу функциясы
def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_kg")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="⬅️ Артка/Назад/Back", callback_data="main_menu")]
    ])

# Негизги менюну алуу
def get_main_menu(lang='kg'):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS[lang]['feedback'], callback_data="send_feedback")],
        [InlineKeyboardButton(text=BUTTONS[lang]['faq'], callback_data="faq")],
        [InlineKeyboardButton(text=BUTTONS[lang]['links'], callback_data="links")],
        [InlineKeyboardButton(text=BUTTONS[lang]['about'], callback_data="about_us")],
        [InlineKeyboardButton(text=BUTTONS[lang].get('change_language', '🌐 Тилди өзгөртүү'), callback_data="change_language")]
    ])

# Шилтемелердин менюсу
def get_links_menu(lang='kg'):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS[lang]['website'], url="https://oshsu.kg")],
        [InlineKeyboardButton(text=BUTTONS[lang]['members'], url="https://studconsul.vercel.app/#members-section")],
        [InlineKeyboardButton(text=BUTTONS[lang]['myedu'], url="https://myedu.oshsu.kg/#/")],
        [InlineKeyboardButton(text=BUTTONS[lang]['instagram'], url="https://www.instagram.com/studenttik_kenesh.oshmu?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==")],
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data="main_menu")]
    ])

# /start командасы
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user.id)
    lang = get_user_language(message.from_user.id)
    
    await message.answer(
        text=TEXTS[lang]['start'].format(name=message.from_user.first_name),
        reply_markup=get_main_menu(lang),
        parse_mode="Markdown"
    )

# Тилди өзгөртүү
@dp.callback_query(F.data == "change_language")
async def change_language(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        text=TEXTS[lang]['choose_language'],
        reply_markup=get_language_keyboard()
    )
    await callback.answer()

# Тилди тандау
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    update_user_language(callback.from_user.id, lang_code)
    
    await callback.message.edit_text(
        text=TEXTS[lang_code]['language_changed'],
        reply_markup=get_main_menu(lang_code)
    )
    await callback.answer()

# Негизги менюго кайтуу
@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        text=TEXTS[lang]['menu'],
        reply_markup=get_main_menu(lang)
    )
    await callback.answer()

# FAQ
@dp.callback_query(F.data == "faq")
async def show_faq(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(
        TEXTS[lang]['faq'], 
        parse_mode="Markdown", 
        disable_web_page_preview=True
    )
    await callback.answer()

# Шилтемелер
@dp.callback_query(F.data == "links")
async def show_links(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(
        TEXTS[lang]['links'], 
        reply_markup=get_links_menu(lang)
    )
    await callback.answer()

# Биз жөнүндө
@dp.callback_query(F.data == "about_us")
async def about_us(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(
        TEXTS[lang]['about'], 
        parse_mode="Markdown"
    )
    await callback.answer()

# Пикир калтыруу
@dp.callback_query(F.data == "send_feedback")
async def ask_feedback(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(TEXTS[lang]['feedback'])
    await callback.answer()

# Пикирди кабыл алуу
@dp.message(F.text)
async def collect_feedback(message: types.Message):
    if message.text.startswith('/'):
        return
    
    lang = get_user_language(message.from_user.id)
    
    # Админге маалымат даярдоо
    feedback_text = TEXTS[lang]['feedback_sent'].format(
        text=message.text,
        name=message.from_user.full_name,
        username=message.from_user.username or "жок",
        user_id=message.from_user.id
    )
    
    try:
        # Админге жөнөтүү
        await bot.send_message(chat_id=ADMIN_ID, text=feedback_text, parse_mode="Markdown")
        await message.answer(TEXTS[lang]['feedback_received'])
    except Exception as e:
        logging.error(f"Ката кетти: {e}")
        await message.answer("Кечиресиз, билдирүү жөнөтүүдө ката кетти.")

# Рассылка командасы
@dp.message(Command("send"))
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    lang = get_user_language(message.from_user.id)
    text_to_send = message.text.replace("/send", "").strip()
    
    if not text_to_send:
        await message.answer(TEXTS[lang]['broadcast_empty'])
        return
    
    users = get_all_users()
    count = 0
    
    for user_id in users:
        try:
            user_lang = get_user_language(user_id)
            await bot.send_message(
                user_id, 
                f"📢 **{TEXTS[user_lang].get('broadcast', 'БИЛДИРҮҮ')}:**\n\n{text_to_send}", 
                parse_mode="Markdown"
            )
            count += 1
        except Exception as e:
            logging.error(f"Ката кетти {user_id}: {e}")
    
    await message.answer(TEXTS[lang]['broadcast_success'].format(count=count))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
