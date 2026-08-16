"""
Sudoku puzzle solving.

Solves Sudoku puzzles using backtracking algorithm.
Can find single or multiple solutions, useful for validation and hints.
"""
from board import create_empty_board, deep_copy, SIZE, EMPTY
from validator import is_safe


def find_empty_cell(board):
    """Find the next empty cell using row-major order.
    
    Optimizations like choosing cell with fewest candidates are possible,
    but row-major is simple and sufficient for typical puzzles.
    
    Args:
        board (list): 9x9 2D list
        
    Returns:
        tuple: (row, col) of first empty cell, or None if no empty cells
    """
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return (row, col)
    return None


def solve(board):
    """Solve a Sudoku puzzle using backtracking.
    
    Modifies the board in-place by filling in the solution.
    Returns True if a solution was found, False if puzzle is unsolvable.
    
    Args:
        board (list): 9x9 2D list with some cells filled
        
    Returns:
        bool: True if puzzle was solved, False if unsolvable
    """
    empty_cell = find_empty_cell(board)
    
    # No empty cells = puzzle is solved
    if empty_cell is None:
        return True
    
    row, col = empty_cell
    
    # Try each number 1-9
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            
            # Recursively solve the rest
            if solve(board):
                return True
            
            # Backtrack if no solution found
            board[row][col] = EMPTY
    
    return False


def solve_copy(puzzle):
    """Solve a puzzle without modifying the original.
    
    Creates a copy of the puzzle, solves it, and returns the solved copy.
    Original puzzle remains unchanged.
    
    Args:
        puzzle (list): 9x9 2D list
        
    Returns:
        list: Solved board, or None if unsolvable
    """
    board = deep_copy(puzzle)
    if solve(board):
        return board
    return None


def count_solutions(puzzle, max_count=2):
    """Count number of solutions a puzzle has.
    
    Useful for validating puzzle uniqueness.
    Stops after finding max_count solutions for efficiency.
    
    Args:
        puzzle (list): 9x9 2D list
        max_count (int): Stop searching after finding this many (default 2)
        
    Returns:
        int: Number of solutions found (up to max_count)
    """
    board = deep_copy(puzzle)
    solutions = [0]  # Use list to allow modification in nested function
    
    def backtrack():
        if solutions[0] >= max_count:
            return  # Stop searching
        
        empty_cell = find_empty_cell(board)
        
        if empty_cell is None:
            solutions[0] += 1
            return
        
        row, col = empty_cell
        
        for num in range(1, SIZE + 1):
            if is_safe(board, row, col, num):
                board[row][col] = num
                backtrack()
                board[row][col] = EMPTY
    
    backtrack()
    return solutions[0]


def has_unique_solution(puzzle):
    """Check if puzzle has exactly one solution.
    
    Useful for validating puzzle quality.
    A valid Sudoku puzzle should have exactly one solution.
    
    Args:
        puzzle (list): 9x9 2D list
        
    Returns:
        bool: True if puzzle has exactly one solution
    """
    return count_solutions(puzzle, max_count=2) == 1


def get_hint(puzzle):
    """Get a hint by revealing one solved cell.
    
    Solves the puzzle and returns the first empty cell's solution.
    Returns None if puzzle is unsolvable or already complete.
    
    Args:
        puzzle (list): 9x9 2D list
        
    Returns:
        dict: {'row': int, 'col': int, 'value': int} or None if no hint
    """
    solved = solve_copy(puzzle)
    if solved is None:
        return None
    
    # Find first empty cell in original puzzle
    for row in range(SIZE):
        for col in range(SIZE):
            if puzzle[row][col] == EMPTY:
                return {
                    'row': row,
                    'col': col,
                    'value': solved[row][col]
                }
    
    return None
