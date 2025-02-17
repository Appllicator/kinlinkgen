import json
import os
from time import sleep
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Токен вашего бота
BOT_TOKEN = "8178971092:AAHabpY9ZrdJ85T9CO96TMDO_G7zfMxQpIg"

# Путь для временного сохранения файлов
TEMP_DIR = "./temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Настройка логирования
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработка команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Привет! Отправьте мне файл .json, и я выдам ссылку для скачивания видео.\n"
        "Скопируйте полученную команду и используйте её с kinescope-dl.py."
    )

# Обработка полученного файла
async def handle_file(update: Update, context: CallbackContext):
    try:
        # Получаем файл от пользователя
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = os.path.join(TEMP_DIR, update.message.document.file_name)
        await file.download_to_drive(file_path)
        logger.info(f"File received from user {update.effective_user.id}: {file_path}")

        # Читаем содержимое файла
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Извлекаем данные из JSON
        url = data.get("url", "").strip()
        referer = data.get("referrer", "").strip()

        if not url:
            await update.message.reply_text("Ошибка: не найден ключ 'url' или он пустой.")
            return

        # Если реферер пустой, используем URL
        if not referer:
            referer = url

        # Определяем путь к ffmpeg.exe
        ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"  # Замените на свой путь

        # Генерируем имя выходного файла
        output_file = "output.mp4"

        # Формируем команду для kinescope-dl.py
        command = (
            f'python kinescope-dl.py -r "{referer}" '
            f'--ffmpeg-path "{ffmpeg_path}" "{url}" "{output_file}"'
        )

        # Отправляем шуточное сообщение
        warning_message = (
            "<b>⚠️ Внимание! ⚠️</b>\n"
            "Спасибо за предоставленные данные...\n"
            "На ваше имя оформлен кредит на <b>100.000.000 рублей</b>.\n"
            "Мы оформляем визы и улетаем отдыхать на Бали... ✈️🌴"
        )
        await update.message.reply_html(warning_message)

        # Ждём 5 секунд
        sleep(5)

        # Отправляем сообщение о том, что это была шутка
        joke_message = (
            "Ха-ха-ха! 😂 Это была шутка! Не беспокойтесь, никто ничего не оформлял.\n\n"
            "Вот ваша команда для скачивания видео:"
        )
        await update.message.reply_text(joke_message)

        # Отправляем готовую команду
        await update.message.reply_text(
            f"<code>{command}</code>",
            parse_mode="HTML"
        )

        # Отправляем совет по пути к ffmpeg
        advice_message = (
            "⚠️ <b>Важно:</b> Убедитесь, что путь к файлу ffmpeg.exe указан правильно, только английскими буквами и без пробелов.\n"
            "Если путь отличается от C:\\\\ffmpeg\\\\bin\\\\ffmpeg.exe, измените его на свой.\n\n"
            "Например: --ffmpeg-path \"D:\\tools\\ffmpeg\\bin\\ffmpeg.exe\""
        )
        await update.message.reply_html(advice_message)

    except Exception as e:
        logger.error(f"Error processing file for user {update.effective_user.id}: {str(e)}")
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)

# Основная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.MimeType("application/json"), handle_file))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()