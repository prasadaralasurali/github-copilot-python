"""Sudoku puzzle generation and solving helpers.

This module provides a small backtracking-based Sudoku generator/solver
used by the Flask app. Functions are intentionally small and testable.
"""

import copy
import random

# Standard 9x9 Sudoku constants
SIZE = 9
EMPTY = 0


def deep_copy(board):
    """Return a deep copy of a 2D `board`.

    This is a thin wrapper around ``copy.deepcopy`` used by the tests
    and to avoid accidental shared references.
    """
    return copy.deepcopy(board)


def create_empty_board():
    """Create and return an empty Sudoku board filled with `EMPTY`.

    The returned board is a list of lists with shape ``SIZE x SIZE``.
    """
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return True if placing `num` at (row, col) does not violate rules.

    Checks the row, column and the 3x3 box containing (row, col).
    """
    # Check row and column for the same number
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
    """Fill the board in-place using randomized backtracking.

    The algorithm attempts to place a safe random number in each empty
    cell and recursively proceeds. Returns True when a full valid
    board is produced, False when no valid completion exists for the
    current partial assignment.
    """
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
                        # backtrack
                        board[row][col] = EMPTY
                # no valid number for this cell
                return False
    # no empty cells -> success
    return True


def find_empty(board):
    """Return the (row, col) of the first empty cell, or None if full.

    The function scans rows then columns and stops at the first
    occurrence of ``EMPTY``.
    """
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == EMPTY:
                return i, j
    return None


def solve_count(board, limit=2):
    """Count Sudoku solutions for `board` up to `limit`.

    This does a backtracking search and returns as soon as the count
    reaches `limit` (useful to test for uniqueness by passing limit=2).
    The `board` is modified during search but callers often pass a
    deep copy to preserve the original.
    """
    pos = find_empty(board)
    if not pos:
        # one valid completed board found
        return 1
    row, col = pos
    count = 0
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            count += solve_count(board, limit)
            board[row][col] = EMPTY
            if count >= limit:
                # early exit when enough solutions found
                return count
    return count


def remove_cells(board, clues):
    """Remove numbers from a fully filled `board` to leave `clues` clues.

    Cells are removed in random order and each removal is validated by
    counting solutions of the resulting puzzle. If a removal produces
    multiple solutions, it is reverted to preserve uniqueness.
    The function modifies ``board`` in-place.
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
            # revert removal when not unique
            board[row][col] = backup
        else:
            filled -= 1
        attempts += 1


def generate_puzzle(clues=35):
    """Generate a puzzle and its solution.

    Returns a tuple ``(puzzle, solution)`` where ``solution`` is a
    fully-filled valid board and ``puzzle`` contains `clues` numbers
    (others set to ``EMPTY``).
    """
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
