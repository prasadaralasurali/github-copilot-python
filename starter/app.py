"""Flask application providing Sudoku endpoints used by the UI tests.

Routes:
- ``/``: renders the `index.html` template.
- ``/new``: generates a new puzzle (accepts ``difficulty`` or ``clues``).
- ``/check``: POST endpoint to compare a submitted board with current solution.

This module keeps a simple in-memory ``CURRENT`` store which is fine for
tests and local development.
"""

from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}


@app.route('/')
def index():
    """Render the main game HTML page."""
    return render_template('index.html')


@app.route('/new')
def new_game():
    """Create a new Sudoku puzzle and store it in ``CURRENT``.

    Supports two query parameters:
    - ``difficulty``: one of ``easy``, ``medium`` (default), or ``hard``.
    - ``clues``: an integer specifying how many clues to leave.

    The endpoint returns JSON with both ``puzzle`` and ``solution``. The
    solution is returned to make it convenient for the browser to offer
    hints and local validation.
    """
    # Accept either numeric 'clues' or a difficulty string: easy/medium/hard
    diff = request.args.get('difficulty')
    if diff:
        diff = diff.lower()
    clues_param = request.args.get('clues')
    if clues_param:
        clues = int(clues_param)
    else:
        if diff == 'easy':
            clues = 40
        elif diff == 'hard':
            clues = 26
        else:
            # default medium
            clues = 32
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    # Return solution too so client can offer hints and local checking
    return jsonify({'puzzle': puzzle, 'solution': solution})


@app.route('/check', methods=['POST'])
def check_solution():
    """Compare a submitted board against the stored solution.

    Expects JSON body with a ``board`` key set to a 9x9 nested list. Returns
    a JSON object listing coordinates for any incorrect cells.
    """
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


if __name__ == '__main__':
    app.run(debug=True)