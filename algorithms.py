from queue import PriorityQueue
from queue import Queue

# DFS Helper Functions


def is_valid_move(grid, row, col, num):
    """Check if placing a number is valid in the current Sudoku grid."""
    size = len(grid)

    # Check row
    if num in grid[row]:
        return False

    # Check column
    for r in range(size):
        if grid[r][col] == num:
            return False

    # Check sub-grid
    box_size = int(size ** 0.5)
    start_row, start_col = row - row % box_size, col - col % box_size
    for i in range(box_size):
        for j in range(box_size):
            if grid[i + start_row][j + start_col] == num:
                return False

    return True


def find_empty_cell(grid):
    """Find the first empty cell (represented by 0) in the Sudoku grid."""
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 0:
                return row, col
    return None


def dfs_solve(grid):
    """Solve the Sudoku puzzle using DFS."""
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True  # Puzzle solved

    row, col = empty_cell

    for num in range(1, len(grid) + 1):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num  # Try placing num in the empty cell

            if dfs_solve(grid):
                return True  # Continue solving if valid

            # Backtrack if the number doesn't lead to a solution
            grid[row][col] = 0

    return False


def heuristic(grid):
    """Heuristic function: count the number of empty cells."""
    return sum(row.count(0) for row in grid)


def valid_moves(grid, row, col):
    """Return a set of valid numbers for a cell."""
    nums = set(range(1, len(grid) + 1))

    # Remove numbers in the current row
    nums -= set(grid[row])

    # Remove numbers in the current column
    nums -= {grid[r][col] for r in range(len(grid))}

    # Remove numbers in the current sub-grid
    box_size = int(len(grid) ** 0.5)
    start_row, start_col = row - row % box_size, col - col % box_size
    for i in range(box_size):
        for j in range(box_size):
            nums.discard(grid[start_row + i][start_col + j])

    return nums


def bfs_solve(grid):
    """Solve the Sudoku puzzle using the BFS algorithm."""
    size = len(grid)
    queue = Queue()
    queue.put(grid)

    while not queue.empty():
        current = queue.get()

        # Find the next empty cell
        empty_cell = find_empty_cell(current)
        if empty_cell is None:
            # Puzzle solved
            for r in range(size):
                for c in range(size):
                    grid[r][c] = current[r][c]
            return True

        row, col = empty_cell

        for num in range(1, size + 1):
            if is_valid_move(current, row, col, num):
                # Create a new grid with the number placed
                new_grid = [r[:] for r in current]
                new_grid[row][col] = num
                queue.put(new_grid)

    return False  # No solution found


def a_star_solve(grid):
    """Solve the Sudoku puzzle using the A* algorithm."""
    size = len(grid)
    pq = PriorityQueue()
    visited = set()

    # Push the initial state
    pq.put((heuristic(grid), grid))

    while not pq.empty():
        _, current = pq.get()

        # Check if the puzzle is solved
        if heuristic(current) == 0:
            for r in range(size):
                for c in range(size):
                    grid[r][c] = current[r][c]
            return True

        # Find the next empty cell
        empty_cell = find_empty_cell(current)
        if empty_cell is None:
            continue

        row, col = empty_cell
        for num in valid_moves(current, row, col):
            new_grid = [r[:] for r in current]  # Deep copy of the grid
            new_grid[row][col] = num
            # Create a hashable representation of the grid
            state_tuple = tuple(map(tuple, new_grid))

            if state_tuple not in visited:
                visited.add(state_tuple)
                pq.put((heuristic(new_grid), new_grid))

    return False  # No solution found


def backtracking_solve(grid, max_num):
    """Solve the Sudoku puzzle using backtracking for a specified grid size."""
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True  # Puzzle solved
    row, col = empty_cell

    for num in range(1, max_num + 1):  # Adjust based on the grid size
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num

            if backtracking_solve(grid, max_num):
                return True

            # If placing num doesn't lead to a solution, reset the cell
            grid[row][col] = 0

    return False  # No valid number can be placed


def evaluate_board(grid):
    """Evaluate the board and return a score based on the number of valid placements."""
    score = 0
    size = len(grid)

    for row in range(size):
        for col in range(size):
            if grid[row][col] == 0:  # Only evaluate empty cells
                # Count valid moves for this cell
                score += len(valid_moves(grid, row, col))
    return score


def minimax(grid, depth, maximizing_player):
    """Minimax algorithm to evaluate the best move."""
    empty_cell = find_empty_cell(grid)
    if not empty_cell or depth == 0:
        return evaluate_board(grid)

    row, col = empty_cell

    if maximizing_player:
        max_eval = float('-inf')
        for num in range(1, len(grid) + 1):
            if is_valid_move(grid, row, col, num):
                grid[row][col] = num  # Try placing num
                # Minimize for the opponent
                eval = minimax(grid, depth - 1, False)
                grid[row][col] = 0  # Undo the move
                max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for num in range(1, len(grid) + 1):
            if is_valid_move(grid, row, col, num):
                grid[row][col] = num  # Try placing num
                # Maximize for the player
                eval = minimax(grid, depth - 1, True)
                grid[row][col] = 0  # Undo the move
                min_eval = min(min_eval, eval)
        return min_eval


def minimax_solve(grid, depth=3):
    """Solve the Sudoku puzzle using the Minimax algorithm."""
    best_score = float('-inf')
    best_move = None

    # Iterate through all empty cells
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True  # Puzzle solved

    row, col = empty_cell

    for num in range(1, len(grid) + 1):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num  # Try placing num
            score = minimax(grid, depth, False)  # Evaluate the move
            grid[row][col] = 0  # Undo the move

            if score > best_score:
                best_score = score
                best_move = (row, col, num)

    if best_move:
        row, col, num = best_move
        grid[row][col] = num  # Place the best number found
        return minimax_solve(grid, depth)  # Continue solving
    return False  # No solution found


def validate_entry(input_value):
    if input_value == "":
        return True  # Allow empty input (backspace)
    elif input_value.isdigit():
        return True
    else:
        return False
