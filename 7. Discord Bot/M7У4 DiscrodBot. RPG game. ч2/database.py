from game_data import locations
import sqlite3
from dataclasses import dataclass


@dataclass
class Player:
    player_id: str
    current_hp: int
    max_hp: int
    damage: int
    current_location_id: int
    passed_locations: str
    current_boss_hp: int


@dataclass
class Location:
    location_id: int
    location_name: str
    boss_name: str
    boss_hp: int
    boss_dmg: int


# Устанавливаем соединение с базой данных "game.db".
# Если базы данных не существует, она будет создана автоматически.
conn = sqlite3.connect("game.db")
cursor = conn.cursor()


def init_db():
    """
    Создает необходимые таблицы в базе данных, если они ещё не существуют.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT UNIQUE,
            current_hp INTEGER,
            max_hp INTEGER,
            damage INTEGER,
            current_location_id INTEGER,
            passed_locations TEXT,
            current_boss_hp INTEGER,
            FOREIGN KEY (current_location_id) REFERENCES locations(location_id)
        )"""
    )

    # Создаём таблицу локаций, если она ещё не существует
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT UNIQUE,
            boss_name TEXT,
            boss_hp INTEGER,
            boss_dmg INTEGER
        )
        """
    )

    # Заполняем таблицу локаций данными, если они ещё не были добавлены
    cursor.executemany(
        """
        INSERT OR IGNORE INTO locations 
        (location_name, boss_name, boss_hp, boss_dmg) 
        VALUES (?, ?, ?, ?)
        """,
        locations,
    )

    # Сохраняем изменения в базе данных
    conn.commit()


def save_player(player_id: str, player_data: tuple[int, int, int, int, str, int]):
    """
    Сохраняет или обновляет данные игрока в базе данных.

    Параметры:
    - `player_id`: Уникальный идентификатор игрока (строка).
    - `player_data`: Кортеж из трех целых чисел, представляющий
        - текущее здоровье игрока,
        - максимальное здоровье игрока,
        - урон игрока,
        - идентификатор текущего места
        - пройденные локации
        - здоровье текущего босса

    Если игрок с указанным `player_id` уже существует, его данные будут обновлены.
    В противном случае будет создана новая запись.
    """
    with conn:
        with conn:
            # Сохраняем или обновляем данные игрока
            cursor.execute(
                """
                INSERT OR REPLACE INTO players 
                (player_id, current_hp, max_hp, damage, current_location_id, passed_locations, current_boss_hp) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (player_id,) + player_data,
            )


def load_player(player_id: str):
    """
    Загружает данные игрока из базы данных по его `player_id`.

    Параметры:
    - `player_id`: Уникальный идентификатор игрока (строка).

    Возвращает:
    - Словарь с параметрами игрока (текущее здоровье, максимальное здоровье, урон), если игрок найден.
    - `None`, если игрок с указанным `player_id` не найден в базе данных.
    """
    cursor.execute(
        """
        SELECT current_hp, max_hp, damage, current_location_id, passed_locations, current_boss_hp
        FROM players
        WHERE player_id = ?
        """,
        (player_id,),
    )

    result: tuple[int, int, int, int, str, int] | None = cursor.fetchone()
    return None if not result else Player(player_id, *result)


def load_location(loc_id: int | None = None, loc_name: str | None = None):
    sql = "SELECT * FROM locations"
    params = ()

    # Если передан id локации, добавляем его в запрос
    if loc_id:
        sql += " WHERE location_id = ?"
        params = (loc_id,)

    # Если передано имя локации, добавляем его в запрос
    elif loc_name:
        sql += " WHERE location_name = ?"
        params = (loc_name,)

    cursor.execute(sql, params)

    result: tuple[int, str, str, int, int] | None = cursor.fetchone()
    return None if not result else Location(*result)


def update_location(player_id: str, loc_id: int):
    with conn:
        cursor.execute(
            "UPDATE players SET current_location_id = ? WHERE player_id = ?",
            (loc_id, player_id),
        )


def update_current_boss_hp(player_id: str, val: int):
    with conn:
        cursor.execute(
            "UPDATE players SET current_boss_hp = ? WHERE player_id = ?",
            (val, player_id),
        )
