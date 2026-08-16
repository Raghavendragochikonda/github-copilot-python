from flask import Flask, render_template, jsonify, request
from puzzle_generator import generate_puzzle
from validator import compare_boards

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

# Map difficulty levels to number of clues
DIFFICULTY_LEVELS = {
    'easy': 45,
    'medium': 35,
    'hard': 25
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    """Generate a new Sudoku puzzle.
    
    Query Parameters:
        difficulty (str): 'easy', 'medium', or 'hard' (default 'medium')
        clues (int): Alternative - number of given numbers (default 35)
                     Clues parameter takes precedence if both provided
    
    Returns:
        JSON with 'puzzle' key containing the puzzle board
    """
    # Check if clues parameter was explicitly provided
    if 'clues' in request.args:
        clues = int(request.args.get('clues'))
    else:
        # Use difficulty level (default medium = 35)
        difficulty = request.args.get('difficulty', 'medium').lower()
        clues = DIFFICULTY_LEVELS.get(difficulty, 35)
    
    puzzle, solution = generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    """Validate only user-entered cells.
    
    Request JSON:
        board: 9x9 2D array with player's answers
        protected: optional list of [row, col] coordinates to ignore
                   (puzzle clues and hinted/locked cells)
    
    Returns:
        JSON with 'incorrect' key containing only incorrect user-entered cells
        OR 400 error if no game is in progress
    """
    data = request.json or {}
    board = data.get('board')
    protected = data.get('protected', [])
    solution = CURRENT.get('solution')
    
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    
    protected_set = set((row, col) for row, col in protected)
    incorrect = []

    for row in range(9):
        for col in range(9):
            if (row, col) in protected_set:
                continue
            if board[row][col] == 0:
                continue
            if board[row][col] != solution[row][col]:
                incorrect.append([row, col])

    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def get_hint():
    """Reveal the correct value for exactly one currently empty cell.

    Request JSON:
        board: 9x9 2D array with the current board state
        row: optional selected row index for the target cell
        col: optional selected col index for the target cell

    Returns:
        JSON with 'row', 'col', and 'value' for a single empty cell
        OR 400 error if there is no active game, the target is not empty,
        or the selected cell is invalid.
    """
    data = request.json or {}
    board = data.get('board')
    row = data.get('row')
    col = data.get('col')
    solution = CURRENT.get('solution')

    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    if not board:
        return jsonify({'error': 'No board provided'}), 400

    if row is None or col is None:
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return jsonify({
                        'row': r,
                        'col': c,
                        'value': solution[r][c]
                    })
        return jsonify({'error': 'No empty cells available'}), 400

    if not isinstance(row, int) or not isinstance(col, int):
        return jsonify({'error': 'Invalid hint coordinates'}), 400

    if row < 0 or row >= 9 or col < 0 or col >= 9:
        return jsonify({'error': 'Hint coordinates out of range'}), 400

    if board[row][col] != 0:
        return jsonify({'error': 'Hint target must be empty'}), 400

    return jsonify({
        'row': row,
        'col': col,
        'value': solution[row][col]
    })

if __name__ == '__main__':
    app.run(debug=True)