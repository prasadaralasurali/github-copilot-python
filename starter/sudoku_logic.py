import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def find_empty(board):
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == EMPTY:
                return i, j
    return None


def solve_count(board, limit=2):
    """Count number of solutions up to `limit` using backtracking."""
    pos = find_empty(board)
    if not pos:
        return 1
    row, col = pos
    count = 0
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            count += solve_count(board, limit)
            board[row][col] = EMPTY
            if count >= limit:
                return count
    return count

def remove_cells(board, clues):
    """Remove cells while ensuring puzzle has a unique solution.

    This function will attempt to remove cells randomly but will
    revert a removal if it produces multiple solutions.
    """
    filled = sum(1 for i in range(SIZE) for j in range(SIZE) if board[i][j] != EMPTY)
    target = clues
    # list of all cell coordinates
    cells = [(i, j) for i in range(SIZE) for j in range(SIZE)]
    random.shuffle(cells)
    attempts = 0
    max_attempts = SIZE * SIZE * 5
    for (row, col) in cells:
        if filled <= target or attempts > max_attempts:
            break
        if board[row][col] == EMPTY:
            continue
        backup = board[row][col]
        board[row][col] = EMPTY
        # make a copy for counting solutions
        board_copy = deep_copy(board)
        sols = solve_count(board_copy, limit=2)
        if sols != 1:
            # revert removal
            board[row][col] = backup
        else:
            filled -= 1
        attempts += 1

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
