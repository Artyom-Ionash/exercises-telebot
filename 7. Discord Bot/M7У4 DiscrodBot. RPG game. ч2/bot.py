from discord.ext import commands
from dotenv import load_dotenv
from game_data import msgs
import database as db
import discord
import os


# --------------------------------------------------------------------------------------------
# Python Discord Bot. Часть 2
#
# Задачи на урок:
# - Создать новую таблицу с данными о локациях и поместить в нее новые данные
# - Обновить ранее созданные таблицы для хранения новых значений
# - Написать функцию для получения данных о локации с использованием id или имени локации
# - Написать функционал для обновления текущей локации и соответствующих ей свойств у игрока.
# --------------------------------------------------------------------------------------------


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
    user = ctx.author
    user_id = str(user.id)

    p = db.load_player(user_id)

    if not p:
        # Учитываем новые свойства
        base_values = (100, 100, 15, 0, "", 0)
        db.save_player(player_id=user_id, player_data=base_values)

        await ctx.send(msgs["welcome"])
    else:
        await ctx.send(msgs["started"].format(user.mention))


@bot.command(name="go")
async def go(ctx: commands.Context, target: str | None = None):
    # Инициализируем значения
    user = ctx.author
    user_id = str(user.id)
    user_mention = user.mention

    # Получаем данные
    p = db.load_player(user_id)

    # Проверяем присутствие игрока в игре
    if not p:
        await ctx.send(msgs["start"].format(user_mention))
        return

    # Проверяем наличие первого параметра
    if target is None:
        await ctx.send(msgs["goerror"].format(user_mention))
        return

    # Получаем информацию по локации, в зависимости от типа аргумента
    l = db.load_location(loc_id=int(target)) if target.isdigit() else db.load_location(loc_name=target)

    # Если такой локации нет, информируем пользователя
    if not l:
        await ctx.send(msgs["wrongloc"].format(user_mention, target))
        return

    # Проверяем, находится ли уже игрок на данной локации
    if l.location_id == p.current_location_id:
        await ctx.send(msgs["alreadyonloc"].format(user_mention, l.location_name))
        return

    # Проверяем, прошел ли уже игрок данную локацию
    passed_locs = p.passed_locations.split(",")
    if str(l.location_id) in passed_locs:
        await ctx.send(msgs["onpassedloc"].format(user_mention, l.location_name))
        return

    # Обновляем текущую локацию и устанавливаем хп босса конкретно для игрока
    db.update_location(player_id=user_id, loc_id=l.location_id)
    db.update_current_boss_hp(player_id=user_id, val=l.boss_hp)

    # Информируем пользователя и передаем данные о локации
    await ctx.send(msgs["bossmeet"].format(user_mention, l.location_name, l.boss_name, l.boss_hp, l.boss_dmg))


if __name__ == "__main__":
    bot.run(token=token)
