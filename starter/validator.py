"""
Sudoku validation and rule checking.

Enforces Sudoku constraints:
- No duplicate numbers in rows
- No duplicate numbers in columns  
- No duplicate numbers in 3x3 boxes
"""
from board import SIZE, BOX_SIZE, EMPTY


def is_safe(board, row, col, num):
    """Check if placing a number at (row, col) violates Sudoku rules.
    
    Validates that the number doesn't conflict with:
    - Other cells in the same row
    - Other cells in the same column
    - Other cells in the same 3x3 box
    
    Args:
        board (list): 9x9 2D list representing current board state
        row (int): Row index (0-8)
        col (int): Column index (0-8)
        num (int): Number to place (1-9)
        
    Returns:
        bool: True if placement is valid, False if it violates rules
    """
    # Check row for duplicate
    for x in range(SIZE):
        if board[row][x] == num:
            return False
    
    # Check column for duplicate
    for x in range(SIZE):
        if board[x][col] == num:
            return False
    
    # Check 3x3 box for duplicate
    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for i in range(BOX_SIZE):
        for j in range(BOX_SIZE):
            if board[start_row + i][start_col + j] == num:
                return False
    
    return True


def is_valid_move(board, row, col, num):
    """Check if a player move is valid.
    
    Wrapper around is_safe() for semantic clarity when validating user moves.
    
    Args:
        board (list): 9x9 2D list representing current board state
        row (int): Row index (0-8)
        col (int): Column index (0-8)
        num (int): Number to place (1-9)
        
    Returns:
        bool: True if move is valid, False otherwise
    """
    # Cell must be empty for a move
    if board[row][col] != EMPTY:
        return False
    
    return is_safe(board, row, col, num)


def find_conflicting_cells(board, protected=None):
    """Return every cell that participates in a Sudoku conflict.

    A conflict exists when two non-zero values in the same row, column,
    or 3x3 box are equal. Protected cells are ignored so puzzle clues and
    hinted/locked entries can stay unchanged while the user edits the rest
    of the board.

    Args:
        board (list): 9x9 board to inspect
        protected (iterable, optional): Coordinates to ignore, such as
            puzzle clues or hinted cells

    Returns:
        list: List of [row, col] coordinates involved in at least one conflict
    """
    protected_set = set((row, col) for row, col in (protected or []))
    conflicts = set()

    def add_conflict(row, col):
        if (row, col) not in protected_set:
            conflicts.add((row, col))

    # Check rows
    for row in range(SIZE):
        seen = {}
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY or (row, col) in protected_set:
                continue
            if value in seen:
                add_conflict(row, seen[value])
                add_conflict(row, col)
            else:
                seen[value] = col

    # Check columns
    for col in range(SIZE):
        seen = {}
        for row in range(SIZE):
            value = board[row][col]
            if value == EMPTY or (row, col) in protected_set:
                continue
            if value in seen:
                add_conflict(seen[value], col)
                add_conflict(row, col)
            else:
                seen[value] = row

    # Check 3x3 boxes
    for start_row in range(0, SIZE, BOX_SIZE):
        for start_col in range(0, SIZE, BOX_SIZE):
            seen = {}
            for row in range(start_row, start_row + BOX_SIZE):
                for col in range(start_col, start_col + BOX_SIZE):
                    value = board[row][col]
                    if value == EMPTY or (row, col) in protected_set:
                        continue
                    if value in seen:
                        first_row, first_col = seen[value]
                        add_conflict(first_row, first_col)
                        add_conflict(row, col)
                    else:
                        seen[value] = (row, col)

    return [[row, col] for row, col in sorted(conflicts)]


def compare_boards(player_board, solution_board):
    """Find all incorrect cells between player and solution boards.
    
    Compares two complete boards and identifies cells where
    the player's answer doesn't match the solution.
    
    Args:
        player_board (list): 9x9 board with player's answers
        solution_board (list): 9x9 board with correct solution
        
    Returns:
        list: List of [row, col] coordinates where boards differ
    """
    incorrect = []
    for i in range(SIZE):
        for j in range(SIZE):
            if player_board[i][j] != solution_board[i][j]:
                incorrect.append([i, j])
    return incorrect


def is_board_complete(board):
    """Check if board is completely filled with no empty cells.
    
    Args:
        board (list): 9x9 2D list
        
    Returns:
        bool: True if all cells are filled, False if any are empty
    """
    for row in board:
        if EMPTY in row:
            return False
    return True


def is_solution_valid(board):
    """Check if a completed board is a valid Sudoku solution.
    
    Verifies that all cells are filled and no Sudoku rules are broken.
    
    Args:
        board (list): 9x9 2D list to validate
        
    Returns:
        bool: True if board is a valid solution, False otherwise
    """
    # Board must be complete
    if not is_board_complete(board):
        return False
    
    # Check each cell doesn't create duplicates
    # (if board was filled correctly, this should always pass)
    for row in range(SIZE):
        for col in range(SIZE):
            num = board[row][col]
            # Temporarily remove the number
            board[row][col] = EMPTY
            # Check if it's safe to place (no duplicates)
            if not is_safe(board, row, col, num):
                board[row][col] = num  # Restore
                return False
            # Restore the number
            board[row][col] = num
    
    return True
