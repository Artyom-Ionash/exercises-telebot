import sqlite3
from uuid import uuid4


def init_db():
    """
    Инициализирует создает таблицу для хранения игровых сессий.

    Создает таблицу "games", если она еще не существует
    (таблица содержит общую информацию об игровых сеансах).
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            user_white_id INTEGER,
            user_black_id INTEGER,
            game_id TEXT,
            won TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def create_game_state_table():
    """
    Инициализирует создает таблицу для хранения состояния игровых досок.

    Создает таблицу "game_state", если она еще не существует
    (таблица содержит детальную информацию каждом игровом сеансе).
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY,
            game_id INTEGER,
            next_black INTEGER,
            game_state TEXT,
        )
    """
    )
    conn.commit()
    conn.close()


def create_game_state(game_id: str, next_black: str, game_state):
    """
    Сохраняет состояние игры в БД.

    Перед вставкой состояние игры преобразуется в строку
    и заменяет одинарные кавычки на двойные для устранения возможных ошибок.

    Args:
        game_id: Уникальный идентификатор игры.
        next_black: Идентификатор "следующего игрока чёрными" (???).
        game_state: Текущее состояние игры, представляемое в виде строки.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    game_state = str(game_state).replace("'", '"')
    query = """
        INSERT INTO game_state (game_id, next_black, game_state)
        VALUES (?, ?, ?)
    """
    cursor.execute(query, (game_id, next_black, game_state))
    conn.commit()
    conn.close()


def update_game_state(game_id: str, next_black: str, game_state):
    """
    Обновляет состояние игры в БД.

    Перед вставкой состояние игры преобразуется в строку
    и заменяет одинарные кавычки на двойные для устранения возможных ошибок.

    Args:
        game_id: Уникальный идентификатор игры.
        next_black: Идентификатор "следующего игрока чёрными" (???).
        game_state: Текущее состояние игры, представляемое в виде строки.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    game_state = str(game_state).replace("'", '"')
    query = """
        UPDATE game_state
        SET next_black = ?, game_state = ?
        WHERE game_id = ?
    """
    cursor.execute(query, (next_black, game_state, game_id))
    conn.commit()
    conn.close()


def get_game_state(game_id: str):
    """
    Получает состояние игры из БД.

    Args:
        game_id: Уникальный идентификатор игры.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT next_black, game_state
        FROM game_state
        WHERE game_id = '{game_id}'
    """
    )
    game_state = cursor.fetchone()
    conn.close()
    return game_state


def create_game(user_white_id: int):
    """
    Создает **новую игру** и сохраняет ее в базе данных.

    Args:
        user_white_id: ID пользователя, который создает игру.

    Returns:
        str: Уникальный идентификатор созданной игры.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    game_id = str(uuid4())  # Генерируем уникальный идентификатор для игры
    cursor.execute(
        f"""
        INSERT INTO games (user_white_id, game_id)
        VALUES ({user_white_id}, '{game_id}')
    """
    )
    conn.commit()
    conn.close()
    return game_id


def game_full(game_id: str):
    """
    Проверяет, **заполнена ли игра**.

    Args:
        game_id: Уникальный идентификатор игры.

    Returns:
        bool: True, если игра полна (в ней есть оба игрока); иначе False.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT user_white_id, user_black_id
        FROM games
        WHERE game_id = '{game_id}'
    """
    )
    users = cursor.fetchone()  # Получаем IDs обоих игроков
    none_or_empty_count = sum(1 for user in users if user is None or user == "")
    conn.close()
    return none_or_empty_count == 0  # Если оба пользователя присутствуют, игра полна


def join_game(user_black_id: str | int, game_id: str):
    """
    Позволяет пользователю присоединиться к игре.

    Args:
        user_black_id: ID пользователя, который хочет присоединиться к игре.
        game_id: Уникальный идентификатор игры, к которой пользователь присоединяется.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""
        UPDATE games
        SET user_black_id = {user_black_id}
        WHERE game_id = '{game_id}'
    """
    )
    conn.commit()
    conn.close()


def get_user_id(game_id: str, color: str):
    """
    Получает ID пользователя по цвету в игре.

    Args:
        game_id: Уникальный идентификатор игры, для которой нужно получить ID.
        color: Цвет игрока ('white' или 'black'), для которого нужно вернуть ID.

    Returns:
        tuple: Кортеж с ID пользователя, если он найден; иначе None.
    """
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT user_{color}_id
        FROM games
        WHERE game_id = '{game_id}'
    """
    )
    user_id: str | None = cursor.fetchone()  # Получаем ID пользователя по указанному цвету
    conn.close()
    return user_id
