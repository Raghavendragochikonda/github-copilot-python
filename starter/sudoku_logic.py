"""
Sudoku Logic - Backward Compatibility Facade

This module maintains backward compatibility by re-exporting all functions
from the modular sub-components:
  - board: Board creation and utilities
  - validator: Sudoku rules and validation
  - puzzle_generator: Puzzle generation
  - solver: Puzzle solving

LEGACY USAGE (still works):
    import sudoku_logic
    puzzle, solution = sudoku_logic.generate_puzzle(35)

MODERN USAGE (recommended):
    from puzzle_generator import generate_puzzle
    from validator import is_safe
    from solver import solve
    puzzle, solution = generate_puzzle(35)
"""

# Re-export from board module
from board import (
    SIZE,
    EMPTY,
    BOX_SIZE,
    create_empty_board,
    deep_copy,
    print_board
)

# Re-export from validator module
from validator import (
    is_safe,
    is_valid_move,
    find_conflicting_cells,
    compare_boards,
    is_board_complete,
    is_solution_valid
)

# Re-export from puzzle_generator module
from puzzle_generator import (
    fill_complete_board,
    remove_clues,
    generate_puzzle,
    generate_puzzle_batch,
    count_solutions
)

# Re-export from solver module (NEW functionality)
from solver import (
    solve,
    solve_copy,
    has_unique_solution,
    get_hint,
    find_empty_cell
)

# Aliases for backward compatibility with old naming
fill_board = fill_complete_board  # Old name -> new name
remove_cells = remove_clues  # Old name -> new name

__all__ = [
    # Constants
    'SIZE',
    'EMPTY',
    'BOX_SIZE',
    # Board utilities
    'create_empty_board',
    'deep_copy',
    'print_board',
    # Validation
    'is_safe',
    'is_valid_move',
    'find_conflicting_cells',
    'compare_boards',
    'is_board_complete',
    'is_solution_valid',
    # Puzzle generation
    'generate_puzzle',
    'fill_complete_board',
    'remove_clues',
    'generate_puzzle_batch',
    # Backward compatibility aliases
    'fill_board',
    'remove_cells',
    # Solving
    'solve',
    'solve_copy',
    'count_solutions',
    'has_unique_solution',
    'get_hint',
    'find_empty_cell',
]
