import os
import sys

# Ensure the project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
import sudoku_logic


def test_find_empty_and_none():
    # empty board -> first empty should be (0,0)
    board = sudoku_logic.create_empty_board()
    pos = sudoku_logic.find_empty(board)
    assert pos == (0, 0)

    # filled board -> no empty cells
    random.seed(10)
    assert sudoku_logic.fill_board(board)
    assert sudoku_logic.find_empty(board) is None


def test_solve_count_on_full_and_single_empty():
    # a fully filled valid board has exactly one solution
    random.seed(11)
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)
    sol_count = sudoku_logic.solve_count(sudoku_logic.deep_copy(board), limit=2)
    assert sol_count == 1

    # remove one cell - typically still unique; ensure solver returns 1
    row, col = 4, 4
    backup = board[row][col]
    board[row][col] = sudoku_logic.EMPTY
    sol_count2 = sudoku_logic.solve_count(sudoku_logic.deep_copy(board), limit=2)
    # For a normal completed Sudoku, removing a single cell should leave a unique
    # possibility for that cell, so solver should return 1.
    assert sol_count2 == 1
    # restore for cleanliness
    board[row][col] = backup
