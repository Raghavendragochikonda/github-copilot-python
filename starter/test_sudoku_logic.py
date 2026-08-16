"""Unit tests for sudoku_logic module."""
import pytest
import sudoku_logic


class TestBoardCreation:
    """Tests for board initialization and structure."""
    
    def test_create_empty_board_dimensions(self):
        """Verify empty board is 9x9."""
        board = sudoku_logic.create_empty_board()
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)
    
    def test_create_empty_board_all_zeros(self):
        """Verify all cells in empty board are EMPTY (0)."""
        board = sudoku_logic.create_empty_board()
        for row in board:
            assert all(cell == sudoku_logic.EMPTY for cell in row)
    
    def test_deep_copy_creates_independent_copy(self):
        """Verify deep_copy creates a separate board object."""
        original = sudoku_logic.create_empty_board()
        original[0][0] = 5
        
        copied = sudoku_logic.deep_copy(original)
        copied[0][0] = 9
        
        # Original should be unchanged
        assert original[0][0] == 5
        assert copied[0][0] == 9


class TestIsSafe:
    """Tests for is_safe() validation function."""
    
    def test_is_safe_empty_board(self):
        """Verify any number is safe on an empty board."""
        board = sudoku_logic.create_empty_board()
        assert sudoku_logic.is_safe(board, 0, 0, 5) is True
        assert sudoku_logic.is_safe(board, 4, 4, 1) is True
    
    def test_is_safe_detects_row_conflict(self):
        """Verify is_safe detects duplicate in same row."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        assert sudoku_logic.is_safe(board, 0, 1, 5) is False
    
    def test_is_safe_detects_column_conflict(self):
        """Verify is_safe detects duplicate in same column."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 3
        assert sudoku_logic.is_safe(board, 1, 0, 3) is False
    
    def test_is_safe_detects_box_conflict(self):
        """Verify is_safe detects duplicate in same 3x3 box."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 7
        # (2, 2) is in the same 3x3 box as (0, 0)
        assert sudoku_logic.is_safe(board, 2, 2, 7) is False
    
    def test_is_safe_allows_different_boxes(self):
        """Verify same number is safe in different 3x3 boxes."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5  # Top-left box
        # (3, 3) is in middle box, should be safe
        assert sudoku_logic.is_safe(board, 3, 3, 5) is True
        # (6, 6) is in bottom-right box, should be safe
        assert sudoku_logic.is_safe(board, 6, 6, 5) is True

    def test_find_conflicting_cells_detects_row_conflict(self):
        """Verify row duplicates are included in conflict detection."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board[0][1] = 5

        conflicts = sudoku_logic.find_conflicting_cells(board)
        assert [0, 0] in conflicts
        assert [0, 1] in conflicts

    def test_find_conflicting_cells_detects_column_conflict(self):
        """Verify column duplicates are included in conflict detection."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board[1][0] = 5

        conflicts = sudoku_logic.find_conflicting_cells(board)
        assert [0, 0] in conflicts
        assert [1, 0] in conflicts

    def test_find_conflicting_cells_detects_box_conflict(self):
        """Verify 3x3 box duplicates are included in conflict detection."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 8
        board[2][2] = 8

        conflicts = sudoku_logic.find_conflicting_cells(board)
        assert [0, 0] in conflicts
        assert [2, 2] in conflicts


class TestRemoveCells:
    """Tests for puzzle creation via cell removal."""
    
    def test_remove_cells_reduces_clues(self):
        """Verify remove_cells reduces board to specified number of clues."""
        board = sudoku_logic.create_empty_board()
        # First, fill the board completely
        sudoku_logic.fill_board(board)
        
        # Count total cells before removal
        cells_before = sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)
        assert cells_before == 81  # All cells filled
        
        # Remove cells to leave 35 clues
        sudoku_logic.remove_cells(board, 35)
        
        # Count remaining cells
        clues = sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)
        assert clues == 35
    
    def test_remove_cells_leaves_empty_cells(self):
        """Verify remove_cells creates empty cells (difficulty)."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        sudoku_logic.remove_cells(board, 40)
        
        empties = sum(1 for row in board for cell in row if cell == sudoku_logic.EMPTY)
        assert empties > 0


class TestGeneratePuzzle:
    """Tests for complete puzzle generation."""
    
    def test_generate_puzzle_returns_two_boards(self):
        """Verify generate_puzzle returns puzzle and solution."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        assert puzzle is not None
        assert solution is not None
    
    def test_generate_puzzle_correct_dimensions(self):
        """Verify both puzzle and solution are 9x9."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        assert len(puzzle) == 9
        assert len(solution) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert all(len(row) == 9 for row in solution)
    
    def test_generate_puzzle_solution_is_complete(self):
        """Verify solution has all 81 cells filled."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        filled = sum(1 for row in solution for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == 81
    
    def test_generate_puzzle_puzzle_is_incomplete(self):
        """Verify puzzle has empty cells (EMPTY = 0)."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        empties = sum(1 for row in puzzle for cell in row if cell == sudoku_logic.EMPTY)
        assert empties > 0
    
    def test_generate_puzzle_with_custom_clues(self):
        """Verify generate_puzzle respects custom clue count."""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=50)
        clues = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert clues == 50
    
    def test_generate_puzzle_puzzle_and_solution_independent(self):
        """Verify puzzle and solution are independent copies."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        puzzle[0][0] = 0  # Modify puzzle
        # Solution should be unaffected
        assert solution[0][0] != 0

    def test_easy_puzzle_has_unique_solution(self):
        """Verify Easy puzzles remain uniquely solvable."""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=45)
        assert sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY) == 45
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert sum(1 for row in solution for cell in row if cell != sudoku_logic.EMPTY) == 81

    def test_medium_puzzle_has_unique_solution(self):
        """Verify Medium puzzles remain uniquely solvable."""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
        assert sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY) == 35
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert sum(1 for row in solution for cell in row if cell != sudoku_logic.EMPTY) == 81

    def test_hard_puzzle_has_unique_solution(self):
        """Verify Hard puzzles remain uniquely solvable."""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=25)
        assert sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY) == 25
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert sum(1 for row in solution for cell in row if cell != sudoku_logic.EMPTY) == 81
