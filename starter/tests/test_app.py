import os
import sys
import json
import random

# Ensure the parent directory (where modules live) is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app_module


def test_index_renders():
    client = flask_app_module.app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<html' in resp.data.lower() or b'<!doctype html' in resp.data.lower()


def test_new_game_and_current_set():
    random.seed(3)
    client = flask_app_module.app.test_client()
    resp = client.get('/new?clues=40')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'puzzle' in data
    puzzle = data['puzzle']
    # basic shape
    assert len(puzzle) == flask_app_module.sudoku_logic.SIZE
    assert flask_app_module.CURRENT['solution'] is not None


def test_check_solution_success_and_failure():
    random.seed(4)
    client = flask_app_module.app.test_client()
    # start new game
    resp = client.get('/new?clues=36')
    assert resp.status_code == 200
    solution = flask_app_module.CURRENT['solution']
    # correct board
    resp = client.post('/check', json={'board': solution})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'incorrect' in data and data['incorrect'] == []
    # make one incorrect cell
    bad = [row[:] for row in solution]
    bad[0][0] = (bad[0][0] % 9) + 1
    resp = client.post('/check', json={'board': bad})
    data = resp.get_json()
    assert len(data['incorrect']) >= 1


def test_check_no_game_in_progress():
    # clear current solution
    flask_app_module.CURRENT['solution'] = None
    client = flask_app_module.app.test_client()
    resp = client.post('/check', json={'board': flask_app_module.sudoku_logic.create_empty_board()})
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
