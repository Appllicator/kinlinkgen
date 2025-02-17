import os
from urllib.parse import urlparse
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json  # Добавьте эту строку

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Порт для вебхука (используется по умолчанию 8443)
PORT = int(os.getenv("PORT", "8080"))

# Создаем приложение с использованием токена
application = Application.builder().token(BOT_TOKEN).build()

# Обработчик команды /start
async def start(update, context):
    await update.message.reply_text(
        "Привет! Отправьте мне файл .json, и я выдам ссылку для скачивания видео."
    )

# Обработчик JSON-файла
async def handle_file(update, context):
    try:
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"./temp/{update.message.document.file_name}"
        os.makedirs("./temp", exist_ok=True)
        await file.download_to_drive(file_path)
        
        # Загрузка JSON-данных
        with open(file_path, 'r') as f:
            data = json.load(f)  # Модуль json должен быть импортирован
        
        playlist_data = data.get("rawOptions", {}).get("playlist", [])
        if not playlist_data:
            await update.message.reply_text("Ошибка: в файле не найден ключ 'rawOptions.playlist'.")
            return
        
        video_url = playlist_data[0].get("sources", {}).get("hls", {}).get("src")
        referer = data.get("referrer") or data.get("url")
        
        if not video_url:
            await update.message.reply_text("Ошибка: не найдена ссылка на видео.")
            return
        
        if not referer:
            parsed_url = urlparse(video_url)
            referer = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Формируем короткую ссылку
        parsed_video_url = urlparse(video_url)
        short_video_url = f"{parsed_url.scheme}://{parsed_video_url.netloc}/{parsed_video_url.path.split('/')[2]}"
        
        # Генерируем команду
        command = (
            f'python kinescope-dl.py -r "{referer}" '
            f'--ffmpeg-path "/path/to/ffmpeg" "{short_video_url}" "output.mp4"'
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
            "Убедитесь, что путь к ffmpeg указан правильно, только английскими буквами и без пробелов.\n"
            "Если путь отличается от /path/to/ffmpeg, измените его на свой."
        )
        await update.message.reply_text(advice_message)
    
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# Настройка вебхука
WEBHOOK_URL = f"https://tg-kinescope-bot.onrender.com/{BOT_TOKEN}"

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.MimeType("application/json"), handle_file))

application.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path=BOT_TOKEN,
    webhook_url=WEBHOOK_URL
)