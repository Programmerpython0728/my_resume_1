import logging
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Database setup
DB_PATH = "data/bot_database.db"
Path("data").mkdir(exist_ok=True)

# Resume file paths
RESUME_FILES = {
    "resume_uzb": "resumes/Khayrullayev_resume_uzb.pdf",
    "resume_eng": "resumes/khayrullayev_resume_english.pdf",
    "resume_rus": "resumes/Khayrullayev_resume_russian.pdf"
}

# Admin ID
ADMIN_ID = int(1585575500)

# Conversation states
WAITING_FOR_RESUME = 1
WAITING_FOR_MESSAGE = 2

# Analytics file
ANALYTICS_FILE = "data/analytics.json"
Path("data").mkdir(exist_ok=True)

# Translations
TRANSLATIONS = {
    "uz": {
        "welcome": "Assalomu alaykum, {name}! 👋\n\nBu bot orqali siz mening resume bilan tanishib chiqishingiz mumkin!\n\n👉 /resume ni bosing.",
        "select_lang": "Til tanlang / Выберите язык / Select language:",
        "choose_resume": "Quyidagi tugmalardan birini tanlang:",
        "resume_uzb": "📄 Resume (O'zbek)",
        "resume_eng": "📄 Resume (English)",
        "resume_rus": "📄 Резюме (Русский)",
        "contact": "📞 Men bilan bog'lanish",
        "contact_text": "📞 Men bilan bog'lanish:\n\n📧 Email: xayrullayevmamur381@gamil.com\n📱 Tel: +998 91 525 07 28\n\nQuyidagi turlardan birini tanlang:",
        "@xayrullayev_0820": "💬 Telegram",
        "https://www.linkedin.com/in/ma-murjon-khayrullayev-3b7465358/": "💼 LinkedIn",
        "back": "🔙 Orqaga",
        "downloaded": "✅ Sizga Xayrullayev Ma'murjoning resumesi yuborildi.\n\nE'tibor bilan tanishib chiqing! 👍",
        "file_not_found": "❌ Resume fayli topilmadi.\n\nIltimos, keyinroq urinib ko'ring yoki admin bilan bog'lanishingiz.",
        "download_error": "❌ Yuklaganda xato yuz berdi. Keyinroq urinib ko'ring.",
        "admin_panel": "🔐 <b>Admin Panel</b>\n\nQuyidagi amallarni tanlang:",
        "update_uzb": "📝 O'zbek resumesini yangilash",
        "update_eng": "📝 English resumesini yangilash",
        "update_rus": "📝 Русское резюме обновить",
        "statistics": "📊 Statistika",
        "users_list": "👥 Foydalanuvchilar ro'yxati",
        "send_msg": "📤 Xabar yuborish",
        "file_info": "📋 Fayl ma'lumotlari",
        "upload_file": "📤 Resume faylini yuboring (PDF):",
        "no_access": "🚫 Sizda bu buyruqni ishlatish huquqi yo'q!",
        "no_file": "❌ Iltimos, PDF fayl yuboring!",
        "updated": "✅ <b>Resume muvaffaqiyatli yangilandi!</b>\n\n📁 Fayl: {file}\n💾 Hajmi: {size:.2f} MB\n⏰ Vaqti: {time}",
        "file_info_text": "📊 <b>Fayl Ma'lumotlari:</b>\n\n{files}",
        "statistics_text": "📈 <b>Statistika:</b>\n\n👥 Jami foydalanuvchilar: {users}\n📥 Jami yuklanishlar: {downloads}\n📅 Oxirgi yangilama: {time}",
        "send_msg_text": "📬 Barcha foydalanuvchilarga xabar yozing:",
        "msg_sent": "✅ <b>Xabar yuborildi!</b>\n\n✔️ Muvaffaqiyatli: {success}\n❌ Xatoli: {failed}",
        "cancelled": "❌ Bekor qilindi.",
        "admin_msg": "📢 <b>Admin xabari:</b>\n\n{msg}",
        "found": "✅",
        "not_found": "❌",
        "users_header": "👥 <b>Foydalanuvchilar ({count}):</b>\n\n",
        "user_info": "<b>👤 {name}</b>\n   ID: {id}\n   Til: {lang}\n   Ro'yxatga olindi: {joined}\n   Oxirgi faollik: {last}\n   Ko'rgan resumeler: {views}\n\n",
    },
    "ru": {
        "welcome": "Здравствуйте, {name}! 👋\n\nС помощью этого бота вы можете ознакомиться с моим резюме!\n\n👉 Нажмите /resume.",
        "select_lang": "Выберите язык / Til tanlang / Select language:",
        "choose_resume": "Выберите один из следующих вариантов:",
        "resume_uzb": "📄 Резюме (Ўзбек)",
        "resume_eng": "📄 Резюме (English)",
        "resume_rus": "📄 Резюме (Русский)",
        "contact": "📞 Связаться со мной",
        "contact_text": "📞 Связаться со мной:\n\n📧 Email: xayrullayevmamur381@gamil.com\n📱 Тел: +998 91 525 07 28\n\nВыберите один из следующих вариантов:",
        "@xayrullayev_0820": "💬 Telegram",
        "https://www.linkedin.com/in/ma-murjon-khayrullayev-3b7465358/": "💼 LinkedIn",
        "back": "🔙 Назад",
        "downloaded": "✅ Резюме Мамуржон Хайруллаев отправлено вам.\n\nПожалуйста, внимательно ознакомьтесь! 👍",
        "file_not_found": "❌ Файл резюме не найден.\n\nПожалуйста, попробуйте позже или свяжитесь с администратором.",
        "download_error": "❌ Ошибка при скачивании. Попробуйте позже.",
        "admin_panel": "🔐 <b>Панель администратора</b>\n\nВыберите действие:",
        "update_uzb": "📝 Обновить резюме (Ўзбек)",
        "update_eng": "📝 Обновить резюме (English)",
        "update_rus": "📝 Обновить резюме (Русский)",
        "statistics": "📊 Статистика",
        "users_list": "👥 Список пользователей",
        "send_msg": "📤 Отправить сообщение",
        "file_info": "📋 Информация о файлах",
        "upload_file": "📤 Отправьте файл резюме (PDF):",
        "no_access": "🚫 У вас нет доступа к этой команде!",
        "no_file": "❌ Пожалуйста, отправьте PDF файл!",
        "updated": "✅ <b>Резюме успешно обновлено!</b>\n\n📁 Файл: {file}\n💾 Размер: {size:.2f} МБ\n⏰ Время: {time}",
        "file_info_text": "📊 <b>Информация о файлах:</b>\n\n{files}",
        "statistics_text": "📈 <b>Статистика:</b>\n\n👥 Всего пользователей: {users}\n📥 Всего загрузок: {downloads}\n📅 Последнее обновление: {time}",
        "send_msg_text": "📬 Напишите сообщение для всех пользователей:",
        "msg_sent": "✅ <b>Сообщение отправлено!</b>\n\n✔️ Успешно: {success}\n❌ Ошибок: {failed}",
        "cancelled": "❌ Отменено.",
        "admin_msg": "📢 <b>Сообщение администратора:</b>\n\n{msg}",
        "found": "✅",
        "not_found": "❌",
        "users_header": "👥 <b>Пользователи ({count}):</b>\n\n",
        "user_info": "<b>👤 {name}</b>\n   ID: {id}\n   Язык: {lang}\n   Зарегистрирован: {joined}\n   Последняя активность: {last}\n   Просмотренные резюме: {views}\n\n",
    },
    "en": {
        "welcome": "Hello, {name}! 👋\n\nYou can view my resume through this bot!\n\n👉 Press /resume.",
        "select_lang": "Select language / Til tanlang / Выберите язык:",
        "choose_resume": "Choose one of the following options:",
        "resume_uzb": "📄 Resume (O'zbek)",
        "resume_eng": "📄 Resume (English)",
        "resume_rus": "📄 Резюме (Русский)",
        "contact": "📞 Contact me",
        "contact_text": "📞 Contact me:\n\n📧 Email: xayrullayevmamur381@gamil.com\n📱 Phone: +998 91 525 07 28\n\nChoose one of the following options:",
        "@xayrullayev_0820": "💬 Telegram",
        "https://www.linkedin.com/in/ma-murjon-khayrullayev-3b7465358/": "💼 LinkedIn",
        "back": "🔙 Back",
        "downloaded": "✅ Ma'murjon Khayrullayev's resume has been sent to you.\n\nPlease review it carefully! 👍",
        "file_not_found": "❌ Resume file not found.\n\nPlease try again later or contact the administrator.",
        "download_error": "❌ Error while downloading. Please try again.",
        "admin_panel": "🔐 <b>Admin Panel</b>\n\nChoose an action:",
        "update_uzb": "📝 Update Resume (O'zbek)",
        "update_eng": "📝 Update Resume (English)",
        "update_rus": "📝 Update Resume (Русский)",
        "statistics": "📊 Statistics",
        "users_list": "👥 Users List",
        "send_msg": "📤 Send Message",
        "file_info": "📋 File Information",
        "upload_file": "📤 Send resume file (PDF):",
        "no_access": "🚫 You don't have access to this command!",
        "no_file": "❌ Please send a PDF file!",
        "updated": "✅ <b>Resume successfully updated!</b>\n\n📁 File: {file}\n💾 Size: {size:.2f} MB\n⏰ Time: {time}",
        "file_info_text": "📊 <b>File Information:</b>\n\n{files}",
        "statistics_text": "📈 <b>Statistics:</b>\n\n👥 Total users: {users}\n📥 Total downloads: {downloads}\n📅 Last update: {time}",
        "send_msg_text": "📬 Write a message for all users:",
        "msg_sent": "✅ <b>Message sent!</b>\n\n✔️ Successful: {success}\n❌ Errors: {failed}",
        "cancelled": "❌ Cancelled.",
        "admin_msg": "📢 <b>Admin message:</b>\n\n{msg}",
        "found": "✅",
        "not_found": "❌",
        "users_header": "👥 <b>Users ({count}):</b>\n\n",
        "user_info": "<b>👤 {name}</b>\n   ID: {id}\n   Language: {lang}\n   Joined: {joined}\n   Last activity: {last}\n   Viewed resumes: {views}\n\n",
    }
}


def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            language TEXT DEFAULT 'uz',
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # User actions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            resume_type TEXT,
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()


def add_or_update_user(user_id: int, first_name: str, last_name: str = None, username: str = None,
                       language: str = "uz"):
    """Add or update user in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, first_name, last_name, username, language)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, first_name, last_name, username, language))

        cursor.execute('''
            UPDATE users SET language = ?, last_activity = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (language, user_id))

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database error: {e}")


def log_user_action(user_id: int, action: str, resume_type: str = None):
    """Log user action in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_actions (user_id, action, resume_type)
            VALUES (?, ?, ?)
        ''', (user_id, action, resume_type))

        cursor.execute('''
            UPDATE users SET last_activity = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database error: {e}")


def get_all_users():
    """Get all users with their info"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.user_id, u.first_name, u.last_name, u.language, 
                   u.joined_date, u.last_activity,
                   COUNT(a.id) as views
            FROM users u
            LEFT JOIN user_actions a ON u.user_id = a.user_id AND a.action = 'download'
            GROUP BY u.user_id
            ORDER BY u.last_activity DESC
        ''')

        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []


def get_user_language(context: CallbackContext) -> str:
    """Get user's selected language"""
    return context.user_data.get('language', 'uz')


def get_text(language: str, key: str, **kwargs) -> str:
    """Get translated text"""
    text = TRANSLATIONS.get(language, TRANSLATIONS['uz']).get(key, key)
    return text.format(**kwargs) if kwargs else text


def load_analytics() -> dict:
    """Load analytics data"""
    try:
        if Path(ANALYTICS_FILE).exists():
            with open(ANALYTICS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Analytics yuklaganda xato: {e}")
    return {"downloads": 0, "users": [], "messages": []}


def save_analytics(data: dict) -> None:
    """Save analytics data"""
    try:
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Analytics saqlaganda xato: {e}")


def language_selection(update: Update, context: CallbackContext) -> None:
    """Show language selection"""
    buttons = [
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ]

    if update.message:
        update.message.reply_text(
            text="Til tanlang / Выберите язык / Select language:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        query = update.callback_query
        query.edit_message_text(
            text="Til tanlang / Выберите язык / Select language:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


def set_language(update: Update, context: CallbackContext) -> None:
    """Set user language"""
    query = update.callback_query
    query.answer()

    lang_map = {
        "lang_uz": "uz",
        "lang_ru": "ru",
        "lang_en": "en"
    }

    lang = lang_map.get(query.data, "uz")
    context.user_data['language'] = lang

    # Update user in database
    user = query.from_user
    add_or_update_user(user.id, user.first_name, user.last_name, user.username, lang)

    start_func(update, context)


def start_func(update: Update, context: CallbackContext) -> None:
    """Handle /start command"""
    user = update.message.from_user if update.message else update.callback_query.from_user
    lang = get_user_language(context)

    # Add/update user in database
    add_or_update_user(user.id, user.first_name, user.last_name, user.username, lang)
    log_user_action(user.id, "start")

    logger.info(f"Yangi foydalanuvchi: {user.id} - {user.first_name} (lang: {lang})")

    text = get_text(lang, "welcome", name=user.first_name)

    if update.message:
        update.message.reply_text(text=text)
        language_selection(update, context)
    else:
        query = update.callback_query
        query.edit_message_text(text=text)
        resume_menu(update, context)


def resume_menu(update: Update, context: CallbackContext) -> None:
    """Handle /resume command"""
    lang = get_user_language(context)

    buttons = [
        [InlineKeyboardButton(text=get_text(lang, "resume_uzb"), callback_data="resume_uzb")],
        [InlineKeyboardButton(text=get_text(lang, "resume_eng"), callback_data="resume_eng")],
        [InlineKeyboardButton(text=get_text(lang, "resume_rus"), callback_data="resume_rus")],
        [InlineKeyboardButton(text=get_text(lang, "contact"), callback_data="contact")],
        [InlineKeyboardButton(text="🌐 " + (
            "Tilni o'zgartirish" if lang == "uz" else "Изменить язык" if lang == "ru" else "Change language"),
                              callback_data="change_lang")]
    ]

    if update.message:
        update.message.reply_text(
            text=get_text(lang, "choose_resume"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        query = update.callback_query
        query.edit_message_text(
            text=get_text(lang, "choose_resume"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )


def download_resume(update: Update, context: CallbackContext) -> None:
    """Handle resume download requests"""
    query = update.callback_query
    query.answer()
    lang = get_user_language(context)

    resume_type = query.data

    if resume_type not in RESUME_FILES:
        query.edit_message_text(text="❌ Xato yuz berdi!")
        return

    file_path = RESUME_FILES[resume_type]

    if not Path(file_path).exists():
        logger.error(f"Resume file not found: {file_path}")
        query.edit_message_text(text=get_text(lang, "file_not_found"))
        return

    try:
        with open(file_path, "rb") as file:
            context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file,
                caption="📎 Resume"
            )

        log_user_action(query.from_user.id, "download", resume_type)
        query.edit_message_text(text=get_text(lang, "downloaded"))

    except Exception as e:
        logger.error(f"Error sending resume: {e}")
        query.edit_message_text(text=get_text(lang, "download_error"))


def contact_handler(update: Update, context: CallbackContext) -> None:
    """Handle contact requests"""
    query = update.callback_query
    query.answer()
    lang = get_user_language(context)

    buttons = [
        [InlineKeyboardButton(text=get_text(lang, "telegram"), url="https://t.me/@xayrullayev_0820")],
        [InlineKeyboardButton(text=get_text(lang, "linkedin"), url="https://www.linkedin.com/in/ma-murjon-khayrullayev-3b7465358/")],
        [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="back_menu")]
    ]

    query.edit_message_text(
        text=get_text(lang, "contact_text"),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def back_to_menu(update: Update, context: CallbackContext) -> None:
    """Go back to main menu"""
    query = update.callback_query
    query.answer()
    resume_menu(update, context)


def change_language_menu(update: Update, context: CallbackContext) -> None:
    """Show language change menu"""
    query = update.callback_query
    query.answer()

    buttons = [
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🔙 " + (
            "Orqaga" if get_user_language(context) == "uz" else "Назад" if get_user_language(
                context) == "ru" else "Back"), callback_data="back_menu")]
    ]

    query.edit_message_text(
        text="Til tanlang / Выберите язык / Select language:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def admin_panel(update: Update, context: CallbackContext) -> None:
    """Show admin panel"""
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("🚫 Sizda bu buyruqni ishlatish huquqi yo'q!")
        return

    buttons = [
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_admin_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_admin_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_admin_en")]
    ]
    update.message.reply_text(
        text="Til tanlang / Выберите язык / Select language:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def show_admin_panel(update: Update, context: CallbackContext) -> None:
    """Show admin panel after language selection"""
    query = update.callback_query
    query.answer()

    lang_map = {
        "lang_admin_uz": "uz",
        "lang_admin_ru": "ru",
        "lang_admin_en": "en"
    }

    lang = lang_map.get(query.data, "uz")
    context.user_data['language'] = lang

    buttons = [
        [InlineKeyboardButton(text=get_text(lang, "update_uzb"), callback_data="update_resume_uzb")],
        [InlineKeyboardButton(text=get_text(lang, "update_eng"), callback_data="update_resume_eng")],
        [InlineKeyboardButton(text=get_text(lang, "update_rus"), callback_data="update_resume_rus")],
        [InlineKeyboardButton(text=get_text(lang, "statistics"), callback_data="statistics")],
        [InlineKeyboardButton(text=get_text(lang, "users_list"), callback_data="users_list")],
        [InlineKeyboardButton(text=get_text(lang, "send_msg"), callback_data="send_message")],
        [InlineKeyboardButton(text=get_text(lang, "file_info"), callback_data="file_info")]
    ]
    query.edit_message_text(
        text=get_text(lang, "admin_panel"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def show_users_list(update: Update, context: CallbackContext) -> None:
    """Show users list"""
    query = update.callback_query
    query.answer()
    lang = get_user_language(context)

    users = get_all_users()

    if not users:
        query.edit_message_text(text="❌ Foydalanuvchilar topilmadi")
        return

    users_text = get_text(lang, "users_header", count=len(users))

    for user in users:
        user_id, first_name, last_name, user_lang, joined_date, last_activity, views = user
        full_name = f"{first_name} {last_name}" if last_name else first_name

        user_info_text = TRANSLATIONS[lang]["user_info"].format(
            name=full_name,
            id=user_id,
            lang=user_lang.upper(),
            joined=datetime.fromisoformat(joined_date).strftime("%Y-%m-%d %H:%M"),
            last=datetime.fromisoformat(last_activity).strftime("%Y-%m-%d %H:%M"),
            views=int(views) if views else 0
        )
        users_text += user_info_text

    # Split if too long
    if len(users_text) > 4096:
        for i in range(0, len(users_text), 4096):
            query.message.reply_text(text=users_text[i:i + 4096], parse_mode="HTML")
    else:
        query.edit_message_text(text=users_text, parse_mode="HTML")


def admin_callback_handler(update: Update, context: CallbackContext) -> int:
    """Handle admin callback queries"""
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        query.answer("🚫 Sizda bu huquq yo'q!", show_alert=True)
        return ConversationHandler.END

    query.answer()
    lang = get_user_language(context)

    if query.data == "file_info":
        files_info = ""
        for name, path in RESUME_FILES.items():
            if Path(path).exists():
                size = Path(path).stat().st_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(Path(path).stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                files_info += f"✅ <b>{name}</b>\n   • Hajmi: {size:.2f} MB\n   • O'zgartirilgan: {mod_time}\n\n"
            else:
                files_info += f"❌ <b>{name}:</b> Topilmadi\n\n"

        query.edit_message_text(
            text=get_text(lang, "file_info_text", files=files_info),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    elif query.data == "statistics":
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_actions WHERE action = 'download'")
        download_count = cursor.fetchone()[0]
        conn.close()

        query.edit_message_text(
            text=get_text(lang, "statistics_text", users=user_count,
                          downloads=download_count, time=datetime.now().strftime('%Y-%m-%d %H:%M')),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    elif query.data == "users_list":
        show_users_list(update, context)
        return ConversationHandler.END

    elif query.data.startswith("update_resume_"):
        resume_type = query.data.replace("update_resume_", "")
        context.user_data['resume_type'] = f"resume_{resume_type}"
        query.edit_message_text(text=get_text(lang, "upload_file"))
        return WAITING_FOR_RESUME

    elif query.data == "send_message":
        query.edit_message_text(text=get_text(lang, "send_msg_text"))
        return WAITING_FOR_MESSAGE

    return ConversationHandler.END


def handle_resume_upload(update: Update, context: CallbackContext) -> int:
    """Handle resume file upload"""
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("🚫 No access!")
        return ConversationHandler.END

    lang = get_user_language(context)

    if not update.message.document:
        update.message.reply_text(get_text(lang, "no_file"))
        return WAITING_FOR_RESUME

    resume_type = context.user_data.get('resume_type')
    if not resume_type:
        update.message.reply_text("❌ Xato yuz berdi.")
        return ConversationHandler.END

    file_path = RESUME_FILES[resume_type]
    file_dir = Path(file_path).parent
    file_dir.mkdir(parents=True, exist_ok=True)

    if Path(file_path).exists():
        try:
            Path(file_path).unlink()
            logger.info(f"Eski fayl o'chirildi: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            update.message.reply_text(f"❌ {str(e)}")
            return ConversationHandler.END

    try:
        new_file = context.bot.get_file(update.message.document.file_id)
        new_file.download(file_path)
        logger.info(f"Yangi resume yuklandi: {file_path}")

        file_size = Path(file_path).stat().st_size / (1024 * 1024)
        update.message.reply_text(
            get_text(lang, "updated", file=file_path, size=file_size, time=datetime.now().strftime('%Y-%m-%d %H:%M')),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error uploading: {e}")
        update.message.reply_text(f"❌ {str(e)}")
        return ConversationHandler.END

    return ConversationHandler.END


def handle_admin_message(update: Update, context: CallbackContext) -> int:
    """Handle admin message to broadcast"""
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("🚫 No access!")
        return ConversationHandler.END

    lang = get_user_language(context)
    message_text = update.message.text

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    if not users:
        update.message.reply_text("❌ No users to send message!")
        return ConversationHandler.END

    success_count = 0
    failed_count = 0

    for user in users:
        user_id = user[0]
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=get_text(lang, "admin_msg", msg=message_text),
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Error sending to {user_id}: {e}")
            failed_count += 1

    update.message.reply_text(
        get_text(lang, "msg_sent", success=success_count, failed=failed_count),
        parse_mode="HTML"
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel operation"""
    lang = get_user_language(context)
    if update.message:
        update.message.reply_text(get_text(lang, "cancelled"))
    return ConversationHandler.END


def error_handler(update: object, context: CallbackContext) -> None:
    """Log errors"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot"""
    # Initialize database
    init_database()

    token = "7657405647:AAG0xjBotjMqN3VBOKs6Yziq2hM6-kXmY64"

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN topilmadi!")

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    # Regular handlers
    dispatcher.add_handler(CommandHandler("start", start_func))
    dispatcher.add_handler(CommandHandler("resume", resume_menu))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))

    # Language selection
    dispatcher.add_handler(CallbackQueryHandler(set_language, pattern="^lang_uz|^lang_ru|^lang_en"))
    dispatcher.add_handler(CallbackQueryHandler(show_admin_panel, pattern="^lang_admin_"))
    dispatcher.add_handler(CallbackQueryHandler(change_language_menu, pattern="^change_lang"))

    # Conversation handler for admin uploads and messages
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_callback_handler, pattern="^update_resume_|^send_message")
        ],
        states={
            WAITING_FOR_RESUME: [
                MessageHandler(Filters.document, handle_resume_upload),
                CommandHandler("cancel", cancel)
            ],
            WAITING_FOR_MESSAGE: [
                MessageHandler(Filters.text & ~Filters.command, handle_admin_message),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(download_resume, pattern="^resume_"))
    dispatcher.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^file_info|^statistics|^users_list"))
    dispatcher.add_handler(CallbackQueryHandler(contact_handler, pattern="^contact"))
    dispatcher.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_menu"))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, resume_menu))

    # Error handler
    dispatcher.add_error_handler(error_handler)

    logger.info("Bot started successfully ✅")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()