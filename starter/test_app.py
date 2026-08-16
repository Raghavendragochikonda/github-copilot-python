"""Integration tests for Flask app routes."""
import pytest
import json
import app as app_module
import sudoku_logic


class TestIndexRoute:
    """Tests for the index page route."""
    
    def test_index_returns_200(self, client):
        """Verify GET / returns status 200."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_returns_html(self, client):
        """Verify GET / returns HTML content type."""
        response = client.get('/')
        assert response.content_type.startswith('text/html')


class TestNewGameRoute:
    """Tests for puzzle generation route."""
    
    def test_new_game_returns_200(self, client):
        """Verify GET /new returns status 200."""
        response = client.get('/new')
        assert response.status_code == 200
    
    def test_new_game_returns_json(self, client):
        """Verify GET /new returns JSON content type."""
        response = client.get('/new')
        assert response.content_type.startswith('application/json')
    
    def test_new_game_returns_puzzle(self, client):
        """Verify GET /new returns a puzzle structure."""
        response = client.get('/new')
        data = json.loads(response.data)
        
        assert 'puzzle' in data
        puzzle = data['puzzle']
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
    
    def test_new_game_puzzle_has_empty_cells(self, client):
        """Verify puzzle has empty cells (difficulty)."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        empties = sum(1 for row in puzzle for cell in row if cell == 0)
        assert empties > 0
    
    def test_new_game_default_clues(self, client):
        """Verify default puzzle has 35 clues."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues == 35
    
    def test_new_game_custom_clues(self, client):
        """Verify custom clue count is respected."""
        response = client.get('/new?clues=50')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues == 50
    
    def test_new_game_stores_state(self, client):
        """Verify /new stores puzzle and solution in CURRENT."""
        client.get('/new')
        
        assert app_module.CURRENT['puzzle'] is not None
        assert app_module.CURRENT['solution'] is not None
        assert len(app_module.CURRENT['puzzle']) == 9
        assert len(app_module.CURRENT['solution']) == 9


class TestCheckSolutionRoute:
    """Tests for solution validation route."""
    
    def test_check_requires_game_in_progress(self, client):
        """Verify POST /check returns 400 if no game active."""
        response = client.post(
            '/check',
            data=json.dumps({'board': [[0] * 9 for _ in range(9)]}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_check_returns_json(self, client):
        """Verify POST /check returns JSON response."""
        client.get('/new')
        response = client.post(
            '/check',
            data=json.dumps({'board': [[0] * 9 for _ in range(9)]}),
            content_type='application/json'
        )
        assert response.content_type.startswith('application/json')
    
    def test_check_correct_solution_has_no_errors(self, client):
        """Verify correct solution returns empty incorrect list."""
        client.get('/new')
        solution = app_module.CURRENT['solution']
        
        response = client.post(
            '/check',
            data=json.dumps({'board': solution}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert 'incorrect' in data
        assert data['incorrect'] == []
    
    def test_check_detects_incorrect_cells(self, client):
        """Verify incorrect cells are identified."""
        client.get('/new')
        solution = app_module.CURRENT['solution']
        
        # Create incorrect board by changing first two cells
        board = [row[:] for row in solution]  # Copy solution
        board[0][0] = (solution[0][0] % 9) + 1  # Change to different number
        board[0][1] = (solution[0][1] % 9) + 1
        
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        incorrect = data['incorrect']
        assert len(incorrect) == 2
        assert [0, 0] in incorrect
        assert [0, 1] in incorrect
    
    def test_check_response_structure(self, client):
        """Verify /check response has correct structure."""
        client.get('/new')
        response = client.post(
            '/check',
            data=json.dumps({'board': [[0] * 9 for _ in range(9)]}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data.get('incorrect'), list)

    def test_check_ignores_blank_and_protected_cells(self, client):
        """Verify only user-entered incorrect cells are reported."""
        client.get('/new')
        solution = [row[:] for row in app_module.CURRENT['solution']]
        board = [row[:] for row in solution]

        board[0][8] = (solution[0][8] % 9) + 1

        response = client.post(
            '/check',
            data=json.dumps({'board': board, 'protected': [[0, 0], [0, 1], [8, 8]]}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert [0, 8] in data['incorrect']
        assert [0, 0] not in data['incorrect']
        assert [0, 1] not in data['incorrect']

    def test_check_keeps_valid_user_entries_unchanged(self, client):
        """Verify valid user-filled cells are not marked incorrect."""
        client.get('/new')
        solution = [row[:] for row in app_module.CURRENT['solution']]
        board = [row[:] for row in solution]

        board[0][8] = (solution[0][8] % 9) + 1
        board[1][1] = solution[1][1]
        board[2][2] = solution[2][2]

        response = client.post(
            '/check',
            data=json.dumps({'board': board, 'protected': [[0, 0], [0, 1], [0, 2]]}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert [0, 8] in data['incorrect']
        assert [1, 1] not in data['incorrect']
        assert [2, 2] not in data['incorrect']


class TestHintRoute:
    """Tests for the hint endpoint."""

    def test_hint_requires_game_in_progress(self, client):
        """Verify POST /hint returns 400 if no game active."""
        response = client.post(
            '/hint',
            data=json.dumps({'board': [[0] * 9 for _ in range(9)]}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_hint_returns_one_correct_empty_cell(self, client):
        """Verify /hint reveals exactly one correct empty cell."""
        client.get('/new?clues=35')
        board = [row[:] for row in app_module.CURRENT['puzzle']]
        response = client.post(
            '/hint',
            data=json.dumps({'board': board}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert set(data.keys()) == {'row', 'col', 'value'}

        row = data['row']
        col = data['col']
        value = data['value']

        assert board[row][col] == 0
        assert app_module.CURRENT['solution'][row][col] == value

    def test_hint_does_not_overwrite_user_input(self, client):
        """Verify hints ignore filled cells and reveal only empty cells."""
        client.get('/new?clues=35')
        board = [row[:] for row in app_module.CURRENT['puzzle']]

        # Fill one empty cell with a user value.
        for row_idx in range(9):
            for col_idx in range(9):
                if board[row_idx][col_idx] == 0:
                    board[row_idx][col_idx] = 5
                    break
            if any(cell == 0 for row in board for cell in row):
                break

        response = client.post(
            '/hint',
            data=json.dumps({'board': board}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert board[data['row']][data['col']] == 0


class TestGameFlow:
    """Integration tests for complete game flow."""
    
    def test_complete_game_flow(self, client):
        """Test a complete flow: new game -> check solution."""
        # Start a new game
        response = client.get('/new?clues=40')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        # Verify puzzle has clues
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues == 40
        
        # Submit the solution (which we stored in CURRENT)
        solution = app_module.CURRENT['solution']
        response = client.post(
            '/check',
            data=json.dumps({'board': solution}),
            content_type='application/json'
        )
        
        # Solution should be correct
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['incorrect'] == []
    
    def test_multiple_games_in_sequence(self, client):
        """Test playing multiple games resets state correctly."""
        # Game 1
        client.get('/new?clues=35')
        response1 = client.get('/new?clues=35')
        data1 = json.loads(response1.data)
        puzzle1 = json.dumps(data1['puzzle'])
        
        # Game 2
        response2 = client.get('/new?clues=35')
        data2 = json.loads(response2.data)
        puzzle2 = json.dumps(data2['puzzle'])
        
        # Puzzles should be different (with high probability)
        # Note: This could theoretically fail, but probability is extremely low
        assert puzzle1 != puzzle2
