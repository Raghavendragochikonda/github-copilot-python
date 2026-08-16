"""
Board utility operations.

Provides low-level board creation, manipulation, and copying.
Defines constants used throughout the Sudoku system.
"""
import copy


# Constants defining Sudoku board dimensions
SIZE = 9
BOX_SIZE = 3
EMPTY = 0


def create_empty_board():
    """Create an empty 9x9 Sudoku board.
    
    Returns:
        list: 9x9 2D list with all cells set to EMPTY (0)
    """
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def deep_copy(board):
    """Create an independent copy of a board.
    
    Modifying the returned board does not affect the original.
    
    Args:
        board (list): 9x9 2D list representing a Sudoku board
        
    Returns:
        list: Independent copy of the board
    """
    return copy.deepcopy(board)


def print_board(board):
    """Pretty-print a Sudoku board for debugging.
    
    Args:
        board (list): 9x9 2D list to print
    """
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        row_str = ""
        for j, cell in enumerate(row):
            if j % 3 == 0 and j != 0:
                row_str += "| "
            row_str += str(cell) if cell != EMPTY else "."
            row_str += " "
        print(row_str)
