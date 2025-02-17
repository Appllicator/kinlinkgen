import os
from urllib.parse import urlparse
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Порт для вебхука (используется по умолчанию 8443)
PORT = int(os.getenv("PORT", "8080"))

# Создаем приложение с использованием токена
application = Application.builder().token(BOT_TOKEN).build()

# Обработчик команды /start
async def start(update, context):
    # Текст приветствия
    welcome_message = (
        "Привет! Отправьте мне файл .json, и я выдам корректную ссылку для скачивания видео "
        "с помощью скрипта kinescope-dl."
    )
    
    # Текст с благодарностью
    thanks_message = (
        "Можете отблагодарить отправив небольшую сумму \n   ❤️НА ШОКОЛАДКУ❤️"
    )
    
    # Кнопка для YooMoney
    keyboard = [
        [InlineKeyboardButton(
            "Поддержать проект",
            url="https://yoomoney.ru/to/4100116398885153"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопкой
    await update.message.reply_text(welcome_message)
    await update.message.reply_text(thanks_message, reply_markup=reply_markup)

# Обработчик JSON-файла
async def handle_file(update, context):
    try:
        # Получаем загруженный файл
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"./temp/{update.message.document.file_name}"
        os.makedirs("./temp", exist_ok=True)  # Создаем временную папку, если её нет
        await file.download_to_drive(file_path)  # Скачиваем файл
        
        # Загрузка JSON-данных
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Извлечение данных из JSON
        video_url = data.get("url")
        referer = data.get("referrer")
        
        if not video_url:
            await update.message.reply_text("Ошибка: в файле не найден ключ 'url'.")
            return
        
        # Если referrer не указан, используем домен из url
        if not referer:
            parsed_url = urlparse(video_url)
            referer = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Генерируем команду
        command = (
            f'python kinescope-dl.py -r "{referer}" '
            f'--ffmpeg-path "/path/to/ffmpeg" "{video_url}" "output.mp4"'
        )
        
        # Шуточное сообщение
        warning_message = (
            "<b>⚠️ Внимание! ⚠️</b>\n"
            "Спасибо за предоставленные данные...\n"
            "На ваше имя оформлен кредит на <b>100.000.000 рублей</b>.\n"
            "Мы оформляем визы и улетаем отдыхать на Бали... ✈️🌴"
        )
        await update.message.reply_html(warning_message)
        
        import time
        time.sleep(5)
        
        # Реальная команда
        joke_message = (
            "Ха-ха-ха! 😂 Это была шутка! Не беспокойтесь, никто ничего не оформлял.\n\n"
            "Вот ваша команда для скачивания видео:"
        )
        await update.message.reply_text(joke_message)
        await update.message.reply_text(
            f"<code>{command}</code>",
            parse_mode="HTML"
        )
        
        advice_message = (
            " ⚠️ Убедитесь, что путь к ffmpeg указан правильно, только английскими буквами и без пробелов.\n"
            "Если путь отличается от /path/to/ffmpeg, измените его на свой."
        )
        await update.message.reply_text(advice_message)
    
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)

# Настройка вебхука
WEBHOOK_URL = f"https://tg-kinescope-bot.onrender.com/{BOT_TOKEN}"

# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.MimeType("application/json"), handle_file))

# Запуск бота через вебхук
application.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path=BOT_TOKEN,
    webhook_url=WEBHOOK_URL
)