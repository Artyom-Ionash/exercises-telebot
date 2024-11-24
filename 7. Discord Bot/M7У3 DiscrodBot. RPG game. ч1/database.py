import sqlite3

# Устанавливаем соединение с базой данных "game.db".
# Если базы данных не существует, она будет создана автоматически.
conn = sqlite3.connect("game.db")
cursor = conn.cursor()


def init_db():
    """
    Создает таблицу игроков в базе данных, если она еще не существует.

    Таблица имеет следующие поля:
    - `id`: Уникальный идентификатор игрока (автоматически увеличивается).
    - `player_id`: Уникальный идентификатор игрока (строка).
    - `current_hp`: Текущее здоровье игрока (целое число).
    - `max_hp`: Максимальное здоровье игрока (целое число).
    - `damage`: Урон, который игрок может нанести (целое число).

    После создания таблицы изменения сохраняются в базе данных.
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT UNIQUE,
            current_hp INTEGER,
            max_hp INTEGER,
            damage INTEGER
        )
        """
    )
    conn.commit()


def save_player(player_id: str, player_data: tuple[int, int, int]):
    """
    Сохраняет или обновляет данные игрока в базе данных.

    Параметры:
    - `player_id`: Уникальный идентификатор игрока (строка).
    - `player_data`: Кортеж из трех целых чисел, представляющий текущее здоровье, максимальное здоровье и урон игрока.

    Если игрок с указанным `player_id` уже существует, его данные будут обновлены.
    В противном случае будет создана новая запись.
    """
    with conn:
        cursor.execute(
            """
                INSERT OR REPLACE INTO players 
                (player_id, current_hp, max_hp, damage) 
                VALUES (?, ?, ?, ?)
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
            SELECT current_hp,
            max_hp,
            damage
            FROM players WHERE player_id = ?
        """,
        (player_id,),
    )

    result: tuple[int, int, int] | None = cursor.fetchone()

    if result:
        current_hp, max_hp, damage = result
        return {"current_hp": current_hp, "max_hp": max_hp, "damage": damage}
    else:
        return None
