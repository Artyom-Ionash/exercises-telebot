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
    l = db.load_locations(loc_id=int(target)) if target.isdigit() else db.load_locations(loc_name=target)

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


@bot.command(name="attack")
async def attack(ctx: commands.Context):
    # Инициализируем значения
    player = ctx.author
    player_id = str(player.id)

    # Получаем данные
    p = db.load_player(player_id)

    if not p:
        await ctx.send(msgs["start"].format(player.mention))
        return

    loc_id = p.current_location_id
    l = db.load_locations(loc_id=loc_id)
    if not l:
        await ctx.send(msgs["noenemy"])
        return

    # Инициализируем значения для удобства
    player_dmg = p.damage
    player_hp = p.current_hp
    boss_name = l.boss_name
    boss_dmg = l.boss_dmg
    boss_hp = p.current_boss_hp
    hp_bonus = l.hp_bonus
    dmg_bonus = l.dmg_bonus

    # Проверяем, не побежден ли уже босс
    if boss_hp == 0:
        await ctx.send(msgs["alreadydead"].format(player.mention, boss_name))
        return

    # Игрок атакует босса
    await ctx.send(msgs["attack"].format(player.mention, boss_name, player_dmg))
    boss_hp -= player_dmg

    # Проверяем, был ли босс побежден
    if boss_hp <= 0:
        # Добавляем локацию в список пройденных
        db.pass_location(player_id=player_id, loc_id=l.location_id)
        await ctx.send(msgs["bossdefeat"].format(boss_name))

        # Добавляем бонусы к характеристикам и восстанавливаем хп
        db.add_bonus(player_id=player_id, hp_bonus=hp_bonus, dmg_bonus=dmg_bonus)
        db.restore_hp(player_id=player_id)

        p = db.load_player(player_id)  # Получаем обновленные данные

        if not p:
            return

        await ctx.send(msgs["bonus"].format(player.mention, p.max_hp, hp_bonus, player_dmg, dmg_bonus))

        # Проверяем, выиграл ли игрок игру
        if db.check_win(passed_locs=p.passed_locations.split(",")):
            await ctx.send(msgs["win"].format(player.mention))
            db.delete_player(player_id)
    else:
        # Босс атакует игрока
        await ctx.send(msgs["attack"].format(boss_name, player.mention, boss_dmg))
        player_hp -= boss_dmg

        # Проверяем, был ли игрок побежден
        if player_hp <= 0:
            await ctx.send(msgs["gameover"].format(player.mention))
            db.delete_player(player_id)
            return

        # Обновляем значения хп в бд
        db.update_hp(player_id=player_id, player_hp=player_hp, boss_hp=boss_hp)
        await ctx.send(msgs["fightstatus"].format(boss_hp, player_hp))


if __name__ == "__main__":
    bot.run(token=token)
