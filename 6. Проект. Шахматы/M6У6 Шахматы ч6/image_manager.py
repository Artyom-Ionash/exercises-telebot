from chess_types import Figure, Position
from PIL import Image
import json

# Константа: смещение для размещения фигур на доске
OFFSET: int = 35

# Отображение буквенных обозначений столбцов в индексы
letters_map = {c: i for i, c in enumerate("ABCDEFGH")}


def translate_position(position: Position) -> tuple[int, int]:
    """
    Преобразует шахматную позицию в координаты на доске.

    :param position: Позиция шахматной фигуры в формате, например, "A1".
    :return: Кортеж с координатами (x, y), где x - номер столбца,
             y - номер строки.
    """
    x = letters_map[position[0].upper()]
    y = 8 - int(position[1])
    return x, y


def place_figure(figure: Figure, position: Position, board: Image.Image) -> Image.Image:
    """
    Размещает изображение шахматной фигуры на доске в заданной позиции.

    :param figure: Имя файла изображения фигуры (например, "knight").
    :param position: Позиция, куда помещается фигура (например, "E4").
    :param board: Объект изображения шахматной доски.
    :return: Обновленный объект изображения шахматной доски с размещенной фигурой.
    """
    chess_piece = Image.open(f"images/{figure}.png")
    x, y = translate_position(position)
    board.paste(chess_piece, (OFFSET + (x * 60), OFFSET + (y * 60)), chess_piece)
    return board


def init_board():
    """
    Рисует шахматную доску с фигурами на начальных позициях.

    :return: Объект изображения шахматной доски с размещёнными фигурами.
    """
    board = Image.open("images/board.png")
    with open("init_positions.json") as f:
        init_positions: dict[Position, Figure] = json.load(f)
    for position, figure in init_positions.items():
        board = place_figure(figure, position, board)
    return board, init_positions


def draw_board(game_state: dict[Position, Figure]):
    """
    Рисует шахматную доску на основе текущего состояния игры.

    :param game_state: Словарь, содержащий текущее состояние игры,
                       где ключами являются позиции фигур, а значениями — сами фигуры.
    :return: Объект изображения шахматной доски с размещёнными фигурами.
    """
    # Открываем изображение шахматной доски из файла
    board = Image.open("images/board.png")

    # Размещаем каждую фигуру на соответствующей позиции на доске в соответствии с состоянием игры
    for position, figure in game_state.items():
        board = place_figure(figure, position, board)

    # Возвращаем обновлённую шахматную доску с фигурами по текущему состоянию
    return board
