COLUMNS = "ABCDEFGH"
ROWS = "12345678"


def is_valid_pawn_move(positions, start, end):

    # Парсим стартовую и конечную позиции
    start_col, start_row = start[0], start[1]
    end_col, end_row = end[0], end[1]

    # Проверяем что позиции находятся на доске
    if start_col not in COLUMNS or end_col not in COLUMNS or start_row not in ROWS or end_row not in ROWS:
        return False

    # Определяем цвет и направление движения пешки
    piece = positions.get(start)
    if not piece or "pawn" not in piece:
        return False

    color = piece.split("-")[0]
    direction = 1 if color == "white" else -1

    # Разница между строками и столбцами
    row_diff = int(end_row) - int(start_row)
    col_diff = COLUMNS.index(end_col) - COLUMNS.index(start_col)

    # Проверяем возможные ходы
    if col_diff == 0:
        # Движение веперед
        if row_diff == direction:
            # Движение на одну клетку вперед
            return end not in positions
        elif row_diff == 2 * direction and start_row in ("2", "7"):
            # Движение на две клетки вперед
            intermediate_row = str(int(start_row) + direction)
            intermediate_pos = start_col + intermediate_row
            return end not in positions and intermediate_pos not in positions
    elif abs(col_diff) == 1 and row_diff == direction:
        # Сьедание фигуры
        return end in positions and color not in positions[end]

    return False


def get_positions_between(start, end):
    start_col, start_row = start[0], int(start[1])
    end_col, end_row = end[0], int(end[1])

    positions = []

    if start_col == end_col:
        # Ветрикальное движение
        for row in range(min(start_row, end_row) + 1, max(start_row, end_row)):
            positions.append(start_col + str(row))
    elif start_row == end_row:
        # горизонтальное движение
        for col in range(min(COLUMNS.index(start_col), COLUMNS.index(end_col)) + 1, max(COLUMNS.index(start_col), COLUMNS.index(end_col))):
            positions.append(COLUMNS[col] + str(start_row))

    return positions


def is_valid_rook_move(positions, start, end):
    # Парсим стартовую и конечную позиции
    start_col, start_row = start[0], start[1]
    end_col, end_row = end[0], end[1]

    # Проверяем что позиции находятся на доске
    if start_col not in COLUMNS or end_col not in COLUMNS or start_row not in ROWS or end_row not in ROWS:
        return False

    # Проверяем что фигура - ладья
    piece = positions.get(start)
    if not piece or "rook" not in piece:
        return False

    # Разница между строками и столбцами
    row_diff = int(end_row) - int(start_row)
    col_diff = COLUMNS.index(end_col) - COLUMNS.index(start_col)

    # Проверяем возможные ходы
    if col_diff == 0 or row_diff == 0:
        # Движение по вертикали или горизонтали
        for pos in get_positions_between(start, end):
            if pos in positions:
                return False
        return True

    return False


def is_valid_knight_move(positions, start, end):
    # Парсим стартовую и конечную позиции
    start_col, start_row = start[0], start[1]
    end_col, end_row = end[0], end[1]

    # Проверяем что позиции находятся на доске
    if start_col not in COLUMNS or end_col not in COLUMNS or start_row not in ROWS or end_row not in ROWS:
        return False

    # Проверяем что фигура - конь
    piece = positions.get(start)
    if not piece or "knight" not in piece:
        return False

    # Разница между строками и столбцами
    row_diff = abs(int(end_row) - int(start_row))
    col_diff = abs(COLUMNS.index(end_col) - COLUMNS.index(start_col))

    # Проверяем возможные ходы
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)


def is_valid_bishop_move(positions, start, end):
    # Парсим стартовую и конечную позиции
    start_col, start_row = start[0], start[1]
    end_col, end_row = end[0], end[1]

    # Проверяем что позиции находятся на доске
    if start_col not in COLUMNS or end_col not in COLUMNS or start_row not in ROWS or end_row not in ROWS:
        return False

    # Проверяем что фигура - слон
    piece = positions.get(start)
    if not piece or "bishop" not in piece:
        return False

    # Разница между строками и столбцами
    row_diff = abs(int(end_row) - int(start_row))
    col_diff = abs(COLUMNS.index(end_col) - COLUMNS.index(start_col))

    # Проверяем возможные ходы
    if row_diff == col_diff:
        # Движение по диагонали
        for pos in get_positions_between(start, end):
            if pos in positions:
                return False
        return True

    return False


def is_valid_queen_move(positions, start, end):
    return is_valid_rook_move(positions, start, end) or is_valid_bishop_move(positions, start, end)


def is_valid_king_move(positions, start, end):
    # Парсим стартовую и конечную позиции
    start_col, start_row = start[0], start[1]
    end_col, end_row = end[0], end[1]

    # Проверяем что позиции находятся на доске
    if start_col not in COLUMNS or end_col not in COLUMNS or start_row not in ROWS or end_row not in ROWS:
        return False

    # Проверяем что фигура - король
    piece = positions.get(start)
    if not piece or "king" not in piece:
        return False

    # Разница между строками и столбцами
    row_diff = abs(int(end_row) - int(start_row))
    col_diff = abs(COLUMNS.index(end_col) - COLUMNS.index(start_col))

    # Проверяем возможные ходы
    return row_diff <= 1 and col_diff <= 1


def is_valid_move(positions, start, end):
    piece = positions.get(start)
    if not piece:
        return False

    if "pawn" in piece:
        return is_valid_pawn_move(positions, start, end)
    elif "rook" in piece:
        return is_valid_rook_move(positions, start, end)
    elif "knight" in piece:
        return is_valid_knight_move(positions, start, end)
    elif "bishop" in piece:
        return is_valid_bishop_move(positions, start, end)
    elif "queen" in piece:
        return is_valid_queen_move(positions, start, end)
    elif "king" in piece:
        return is_valid_king_move(positions, start, end)
    return False


def is_check(positions, color):
    king = ("white" if color == "black" else "black") + "-king"
    king_pos = None
    for pos, piece in positions.items():
        if king == piece:
            king_pos = pos
            break

    for pos, piece in positions.items():
        if color not in piece:
            continue

        if is_valid_move(positions, pos, king_pos):
            return True

    return False


def is_checkmate(positions, color):
    king = color + "-king"
    king_pos = None
    for pos, piece in positions.items():
        if king == piece:
            king_pos = pos
            break

    if not king_pos:
        return True

    return False
