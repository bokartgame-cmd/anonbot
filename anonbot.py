import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = '8528321647:AAH4seaUFWTD68eKoJuBY3TO8F8tsuSqBGs'
ADMIN_ID = '1394626253'

bot = telebot.TeleBot(TOKEN)


def check_admin_id():
    """Проверка и получение ID админа"""
    if ADMIN_ID == 'ВАШ_ID_ПОЛЬЗОВАТЕЛЯ':
        logger.error("Не установлен ADMIN_ID!")
        return None
    try:
        return int(ADMIN_ID)
    except ValueError:
        logger.error("ADMIN_ID должен быть числом!")
        return None


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
👋 Добро пожаловать в анонимный прием сообщений!

📨 Отправьте любое сообщение (текст, фото, документ) - оно будет переслано администратору.

Команды:
/start - это сообщение

"""
    bot.reply_to(message, welcome_text)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        admin_id = check_admin_id()
        if not admin_id:
            bot.reply_to(message, "❌ Ошибка в настройках бота. Свяжитесь с разработчиком.")
            return

        # Логируем (без персональных данных)
        logger.info(f"Получен текст от пользователя {message.from_user.id}, длина: {len(message.text)}")

        # Формируем сообщение для админа
        admin_message = f"📨 Анонимное сообщение:\n\n{message.text}\n\n---\n"

        # Пытаемся отправить админу
        bot.send_message(admin_id, admin_message)

        # Подтверждаем пользователю
        bot.reply_to(message, "✅ Ваше сообщение отправлено анонимно!")
        logger.info(f"Сообщение успешно переслано админу {admin_id}")

    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Ошибка Telegram API: {e}")
        if "chat not found" in str(e):
            bot.reply_to(message, "❌ Администратор не найден. Бот не настроен.")
        else:
            bot.reply_to(message, f"❌ Ошибка отправки: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        bot.reply_to(message, "❌ Произошла неизвестная ошибка.")


@bot.message_handler(content_types=['photo', 'document', 'audio', 'voice', 'video'])
def handle_media(message):
    try:
        admin_id = check_admin_id()
        if not admin_id:
            bot.reply_to(message, "❌ Ошибка в настройках бота.")
            return

        caption = message.caption or "Без описания"
        logger.info(f"Получено медиа от {message.from_user.id}, тип: {message.content_type}")

        # Формируем описание для админа
        media_info = f"📨 Анонимное сообщение ({message.content_type})\n\nОписание: {caption}\n\n---\nID отправителя: {message.from_user.id}"

        # Пересылаем медиафайл
        if message.photo:
            bot.send_photo(admin_id, message.photo[-1].file_id, caption=media_info)
        elif message.document:
            bot.send_document(admin_id, message.document.file_id, caption=media_info)
        elif message.audio:
            bot.send_audio(admin_id, message.audio.file_id, caption=media_info)
        elif message.voice:
            bot.send_voice(admin_id, message.voice.file_id, caption=media_info)
        elif message.video:
            bot.send_video(admin_id, message.video.file_id, caption=media_info)

        bot.reply_to(message, "✅ Ваше медиа-сообщение отправлено!")

    except Exception as e:
        logger.error(f"Ошибка отправки медиа: {e}")
        bot.reply_to(message, "❌ Ошибка отправки медиафайла.")


@bot.message_handler(func=lambda message: True)
def handle_all(message):
    bot.reply_to(message, "❓ Отправьте текст, фото или документ для анонимной отправки.")


if __name__ == '__main__':
    logger.info("Бот запускается...")

    # Проверка конфигурации
    admin_id = check_admin_id()
    if admin_id:
        try:
            bot.send_message(admin_id, "🤖 Бот анонимных сообщений запущен и готов к работе!")
            logger.info(f"Уведомление отправлено админу {admin_id}")
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление админу: {e}")

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")

    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")