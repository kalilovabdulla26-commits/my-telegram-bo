import asyncio
import logging
import sqlite3  # Маалымат базасы үчүн кошулду
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Сиздин токениңиз жана ID
API_TOKEN = '8273226401:AAFJgyvNaskohUZTpxY64jy5np-7q4eH5HM'
ADMIN_ID = 5148336517  # @userinfobot берген сиздин жеке ID номериңиз

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- МҮЧӨЛӨРДҮН БАЗАСЫН БАШКАРУУ (Кошумча) ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

init_db()

# --- 1. БОТТУН БАШКЫ МЕНЮСУ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user.id)  # Колдонуучуну базага кошуу
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Сунуш же пикир калтыруу", callback_data="send_feedback")],
        [InlineKeyboardButton(text="❓ Көп берилүүчү суроолор (FAQ)", callback_data="faq")],
        [InlineKeyboardButton(text="🔗 Пайдалуу шилтемелер", callback_data="links")],
        [InlineKeyboardButton(text="ℹ️ Биз жөнүндө", callback_data="about_us")]
    ])
    
    await message.answer(
        text=f"Салам, {message.from_user.first_name}! 👋\n\nБул **ОшМУ Студенттик кеңешинин** расмий боту. "
             f"Төмөнкү бөлүмдөрдүн бирин тандаңыз:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# --- 2. FAQ БӨЛҮМҮ (Суроо-Жооп) ---
@dp.callback_query(F.data == "faq")
async def show_faq(callback: types.CallbackQuery):
    faq_text = (
        "❓ **Көп берилүүчү суроолор:**\n\n"
        "1️⃣ **Контрактты кайдан төлөйм?**\n"
        "— MyEDU платформасынан жеке эсеп алып аны Finca BANKтын терминалдары аркылуу төлөй аласыз.\n\n"
        "2️⃣ **2025-2026-окуу жылына контракт баалары кандай?**\n"
        "— Контракт баалары боюнча толук прейскурантты бул жерден көрө аласыз: "
        "[Контракт бааларын көрүү (PDF)](https://www.oshsu.kg/storage/uploads/files/21752775966preyskursant_zhany_2025-2026_okuu_zhylyna.pdf)\n"
    )
    # disable_web_page_preview=True кылсаң, PDFтин сүрөтү чыгып экранды ээлебейт
    await callback.message.answer(faq_text, parse_mode="Markdown", disable_web_page_preview=True)
    await callback.answer()

# --- 3. ПАЙДАЛУУ ШИЛТЕМЕЛЕР ---
@dp.callback_query(F.data == "links")
async def show_links(callback: types.CallbackQuery):
    links_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 ОшМУ расмий сайт", url="https://oshsu.kg")],
        [InlineKeyboardButton(text="🌐 ОшМУ студенттик кеңешинин курамы", url="https://studconsul.vercel.app/#members-section")],
        [InlineKeyboardButton(text="📚 MyEDU", url="https://myedu.oshsu.kg/#/")],
        [InlineKeyboardButton(text="📸 Инстаграм баракчабыз", url="https://www.instagram.com/studenttik_kenesh.oshmu?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==")]
    ])
    await callback.message.answer("Керектүү шилтемени тандаңыз: 👇", reply_markup=links_markup)
    await callback.answer()

# --- 4. БИЗ ЖӨНҮНДӨ ---
@dp.callback_query(F.data == "about_us")
async def about_us(callback: types.CallbackQuery):
    about_text = (
        "🏢 **Студенттик кеңеш жөнүндө**\n\n"
        "**Студенттик кеңеш** — бул жогорку окуу жайдагы студенттердин өз алдынча уюштурулган органы. "
        "Негизги максаты — студенттердин кызыкчылыгын коргоо, иш-чараларды уюштуруу жана "
        "администрация менен студенттерди байланыштыруучу көпүрө болуу.\n\n"
        "✅ **Негизги функциялары:**\n"
        "🔹 Окуу жайдагы маселелерди жетекчиликке жеткирүү;\n"
        "🔹 Маданий, спорттук, социалдык иш-чараларды уюштуруу;\n"
        "🔹 Жаңы студенттерге жардам берүү (адаптация, багыт берүү);\n"
        "🔹 Стипендия, жатакана маселелеринде колдоо көрсөтүү;\n"
        "🔹 Коомдук иштерге студенттерди тартуу.\n\n"
        "📜 **Тарыхы:**\n"
        "Окуу жайдагы жаштар уюмунун тарыхы 1951-жылы Ош пединституту түзүлгөндөн тартып башталат. "
        "1992-жылы комсомол комитетинин ордуна **студенттик сенат** түзүлгөн. "
        "Ал эми 2000-жылдын 10-декабрындагы КР Президентинин указына ылайык, студенттик сенат **жаштар комитети** болуп кайрадан түзүлгөн.\n\n"
        "🚀 Азыркы учурда жаштар комитети студенттер менен жетекчилерди тыгыз байланыштырган миссияны аркалап, "
        "студенттердин кадыр-барктуу уюму катары иш алып барууда.\n\n"
    )
    
    await callback.message.answer(about_text, parse_mode="Markdown")
    await callback.answer()

# --- РАССЫЛКА КОМАНДАСЫ (Кошумча) ---
@dp.message(Command("send"))
async def broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        text_to_send = message.text.replace("/send", "").strip()
        if not text_to_send:
            await message.answer("Сураныч, текстти кошо жазыңыз. Мисалы: `/send Салам студенттер!`")
            return

        users = get_all_users()
        count = 0
        for user_id in users:
            try:
                await bot.send_message(user_id, f"📢 **МААНИЛҮҮ КУЛАКТАНДЫРУУ:**\n\n{text_to_send}", parse_mode="Markdown")
                count += 1
            except Exception:
                pass
        await message.answer(f"Билдирүү {count} колдонуучуга жөнөтүлдү! ✅")

# --- 5. ПИКИР КАБЫЛ АЛУУ ЖАНА АДМИНГЕ ЖӨНӨТҮҮ ---
@dp.callback_query(F.data == "send_feedback")
async def ask_feedback(callback: types.CallbackQuery):
    await callback.message.answer("Сураныч, сунушуңузду же пикириңизди жазып жөнөтүңүз. 👇")
    await callback.answer()

@dp.message()
async def collect_feedback(message: types.Message):
    if message.text and not message.text.startswith('/'):
        # Админге маалымат даярдоо
        user_info = f"👤 Кимден: {message.from_user.full_name} (@{message.from_user.username})\n🆔 ID: {message.from_user.id}"
        feedback_text = f"📩 **ЖАҢЫ ПИКИР КЕЛДИ:**\n\n\"{message.text}\"\n\n{user_info}"
        
        try:
            # Сизге (админге) жөнөтүү
            await bot.send_message(chat_id=ADMIN_ID, text=feedback_text, parse_mode="Markdown")
            await message.answer("Рахмат! Сиздин билдирүүңүз кабыл алынды жана каралат. ✅")
        except Exception as e:
            logging.error(f"Ката кетти: {e}")
            await message.answer("Кечиресиз, билдирүү жөнөтүүдө ката кетти. Сураныч, кийинчерээк аракет кылып көрүңүз.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())