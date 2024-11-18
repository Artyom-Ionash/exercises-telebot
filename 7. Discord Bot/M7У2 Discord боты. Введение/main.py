import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from deep_translator import GoogleTranslator  # Импортируем клиент переводчика


load_dotenv()  # Загружаем переменные окружения из файла .env
token = os.getenv(key="TOKEN")  # Получаем токен бота из переменной окружения
if not token:
    raise ValueError(f"Токен бота не найден. Убедитесь, что в файле /.env переменная окружения TOKEN установлена.")

# Создаем объект intents, чтобы указать, какие события бот будет получать
intents = discord.Intents.default()  # Задаём стандартные свойства
intents.message_content = True  # Включаем возможность получения сообщений

# Создаем объект бота с заданными правами и префиксом команд
bot = commands.Bot(intents=intents, command_prefix="!")


# Обработчик события вызывается, когда бот успешно подключается к Discord
@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен и готов к работе!")


# Определяем команду бота с именем 'hello'
@bot.command(name="hello")
async def greet(ctx: commands.Context):
    # Отправляем приветственное сообщение в канал, откуда была вызвана команда
    await ctx.send(f"Привет, {ctx.author.name}! Чем я могу помочь?")


@bot.command(name="translate")
async def translate_text(ctx: commands.Context, lang: str, *, text: str) -> None:
    """
    Переводит заданный текст на указанный язык.

    Аргументы:
    ctx (commands.Context): Контекст команды, который включает информацию о вызове команды.
    lang (str): Код языка, на который необходимо перевести текст (например, 'en' для английского, 'ru' для русского).
    text (str): Текст, который нужно перевести.

    Примеры использования:
    - !translate en Привет, как дела?  # Переведет на английский
    - !translate ru Hello, how are you?  # Переведет на русский

    Исключения:
    Если во время перевода возникнет ошибка, будет отправлено сообщение с описанием ошибки.
    """
    try:
        # Переводим текст на указанный язык (автоматически определяем исходный язык)
        translation = GoogleTranslator(source="auto", target=lang).translate(text)
        # Отправляем перевод пользователю
        await ctx.send(f"Перевод на {lang}: {translation}")
    except Exception as e:
        # Если возникла ошибка при переводе, выводим информацию
        error_message = f"Произошла ошибка: {str(e)}"
        if len(error_message) > 1950:
            error_message = error_message[:1950] + "✂️ (Текст обрезан из-за большого объема)"
        await ctx.send(error_message)


# Запускаем бота, передавая ему токен для подключения к Discord
if __name__ == "__main__":
    bot.run(token=token)
