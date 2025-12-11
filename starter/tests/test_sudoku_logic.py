import os
import sys
import random

# Ensure the parent directory (where modules live) is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sudoku_logic


def valid_board(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    # rows
    for r in range(sudoku_logic.SIZE):
        assert set(board[r]) == expected
    # cols
    for c in range(sudoku_logic.SIZE):
        col = {board[r][c] for r in range(sudoku_logic.SIZE)}
        assert col == expected
    # boxes
    for br in range(0, sudoku_logic.SIZE, 3):
        for bc in range(0, sudoku_logic.SIZE, 3):
            box = set()
            for r in range(3):
                for c in range(3):
                    box.add(board[br + r][bc + c])
            assert box == expected


def test_deep_copy_independent():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    cp = sudoku_logic.deep_copy(board)
    cp[0][0] = 7
    assert board[0][0] == 5
    assert cp[0][0] == 7


def test_create_empty_board():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_basic():
    board = sudoku_logic.create_empty_board()
    board[0][1] = 3
    board[1][0] = 4
    # same row
    assert not sudoku_logic.is_safe(board, 0, 2, 3)
    # same column
    assert not sudoku_logic.is_safe(board, 2, 0, 4)
    # box conflict
    board[1][1] = 6
    assert not sudoku_logic.is_safe(board, 2, 2, 6)
    # safe
    assert sudoku_logic.is_safe(board, 2, 2, 5)


def test_fill_board_and_validity():
    random.seed(0)
    board = sudoku_logic.create_empty_board()
    ok = sudoku_logic.fill_board(board)
    assert ok is True
    # no empty cells
    assert all(cell != sudoku_logic.EMPTY for row in board for cell in row)
    # validity checks
    valid_board(board)


def test_remove_cells_counts():
    random.seed(1)
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)
    full_count = sum(1 for r in board for c in r if c != sudoku_logic.EMPTY)
    # remove to a specific number of clues
    clues = 30
    sudoku_logic.remove_cells(board, clues)
    remaining = sum(1 for r in board for c in r if c != sudoku_logic.EMPTY)
    assert remaining == clues


def test_generate_puzzle_solution_and_puzzle():
    random.seed(2)
    puzzle, solution = sudoku_logic.generate_puzzle(clues=32)
    # shapes
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    # solution is a valid filled board
    valid_board(solution)
    # puzzle has correct number of clues
    clues = sum(1 for r in puzzle for c in r if c != sudoku_logic.EMPTY)
    assert clues == 32
