"""
Sudoku puzzle generation.

Generates random valid Sudoku puzzles by:
1. Creating a complete valid board
2. Removing numbers to create playable puzzles
3. Ensuring puzzle has unique solution
"""
import random
from board import create_empty_board, deep_copy, SIZE, EMPTY
from validator import is_safe


def find_empty_cell(board):
    """Return the first empty cell in row-major order."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return (row, col)
    return None


def count_solutions(board, max_solutions=2):
    """Count valid Sudoku solutions, stopping once the limit is reached."""
    working = deep_copy(board)
    solutions_found = 0

    def backtrack():
        nonlocal solutions_found
        if solutions_found >= max_solutions:
            return

        empty_cell = find_empty_cell(working)
        if empty_cell is None:
            solutions_found += 1
            return

        row, col = empty_cell
        for num in range(1, SIZE + 1):
            if is_safe(working, row, col, num):
                working[row][col] = num
                backtrack()
                working[row][col] = EMPTY
                if solutions_found >= max_solutions:
                    return

    backtrack()
    return solutions_found


def fill_complete_board(board):
    """Fill a board with a valid complete Sudoku solution using backtracking.
    
    Randomly fills all 81 cells respecting Sudoku constraints.
    Uses randomized candidate selection for varied puzzle generation.
    
    Args:
        board (list): 9x9 2D list (should start empty)
        
    Returns:
        bool: True if board was successfully filled, False if impossible
    """
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                # Get random order of candidates (1-9)
                candidates = list(range(1, SIZE + 1))
                random.shuffle(candidates)
                
                for num in candidates:
                    if is_safe(board, row, col, num):
                        board[row][col] = num
                        
                        # Recursively fill the rest
                        if fill_complete_board(board):
                            return True
                        
                        # Backtrack: undo placement
                        board[row][col] = EMPTY
                
                # No valid candidate found, backtrack
                return False
    
    # All cells filled successfully
    return True


def remove_clues(board, num_clues):
    """Remove numbers from a complete board to create a unique Sudoku puzzle.
    
    Each candidate removal is validated by checking whether the puzzle still has
    exactly one solution. If more than one solution is possible, the value is
    restored so the generated puzzle remains uniquely solvable.
    
    The function attempts to reduce the board to the requested clue count while
    preserving uniqueness. Because some solved boards cannot reach a given clue
    count without breaking uniqueness, callers may retry with a fresh board.
    
    Args:
        board (list): 9x9 2D list (complete solution)
        num_clues (int): Number of cells to keep (typically 17-40)
                         Lower = harder, Higher = easier
    """
    cells_to_remove = SIZE * SIZE - num_clues
    candidate_cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(candidate_cells)

    while cells_to_remove > 0 and candidate_cells:
        row, col = candidate_cells.pop()
        if board[row][col] == EMPTY:
            continue

        removed_value = board[row][col]
        board[row][col] = EMPTY

        if count_solutions(board) != 1:
            board[row][col] = removed_value
            continue

        cells_to_remove -= 1

    return sum(1 for row in board for cell in row if cell != EMPTY) == num_clues


def generate_puzzle(clues=35):
    """Generate a random Sudoku puzzle with specified difficulty.
    
    Creates a valid puzzle by:
    1. Generating a complete solution
    2. Removing numbers to create puzzle
    
    Args:
        clues (int): Number of given numbers in puzzle (default 35)
                     Typical range: 17-40
                     17 = very hard, 35 = medium, 40+ = easy
    
    Returns:
        tuple: (puzzle, solution) where:
            - puzzle: 9x9 board with empty cells (clues given)
            - solution: 9x9 board completely filled (unique solution)
    """
    for _ in range(100):
        solution_board = create_empty_board()
        fill_complete_board(solution_board)
        solution = deep_copy(solution_board)

        puzzle_board = deep_copy(solution_board)
        if remove_clues(puzzle_board, clues):
            return deep_copy(puzzle_board), solution

    raise RuntimeError(f"Unable to generate a unique Sudoku puzzle with {clues} clues")


def generate_puzzle_batch(count, clues=35):
    """Generate multiple puzzles in batch.
    
    Useful for pre-generating puzzles or testing.
    
    Args:
        count (int): Number of puzzles to generate
        clues (int): Number of clues per puzzle (default 35)
        
    Returns:
        list: List of (puzzle, solution) tuples
    """
    puzzles = []
    for _ in range(count):
        puzzle, solution = generate_puzzle(clues)
        puzzles.append((puzzle, solution))
    return puzzles
