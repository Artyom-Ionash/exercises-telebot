from discord.ext import commands
from dotenv import load_dotenv
from game_data import msgs
import database as db
import discord
import os

db.init_db()

load_dotenv()
token = os.getenv(key="TOKEN")
if not token:
    raise ValueError(f"Токен бота не найден. Убедитесь, что в файле /.env переменная окружения TOKEN установлена.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(msgs["ready"].format(bot.user))


@bot.command(name="start")
async def start_game(ctx: commands.Context):
    # Инициализируем значения
    player = ctx.author
    player_id = str(player.id)

    # Получаем данные
    player_data = db.load_player(player_id)

    if not player_data:  # Если игрок еще не в игре, добавляем стартовые данные в бд
        base_values = (100, 100, 15)
        db.save_player(player_id=player_id, player_data=base_values)

        # Информируем пользователя
        await ctx.send(msgs["welcome"])

    else:  # Если игрок уже начал, отправляем сообщение
        await ctx.send(msgs["started"].format(player.mention))


if __name__ == "__main__":
    bot.run(token=token)
