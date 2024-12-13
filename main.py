from globalVariables import *
from algorithms import *
import random
import time
import tkinter as tk
from tkinter import messagebox


def update_grid_with_solution():
    """Update the grid with the solved values and highlight solved cells."""
    for row in range(len(user_grid)):
        for col in range(len(user_grid[row])):
            entries[row][col].delete(0, tk.END)  # Clear the entry box
            entries[row][col].insert(
                0, str(user_grid[row][col]))  # Insert solved value
            # Highlight solved cells
            entries[row][col].config(state='disabled', bg="light green")

# Create grid for the Sudoku board


def create_grid(size, pre_filled_grid):
    """Create a Sudoku grid based on the size and pre-filled values."""
    # Clear previous entries if any
    for entry_row in entries:
        for entry in entry_row:
            entry.destroy()
    entries.clear()

    # Reinitialize user_grid based on the grid size
    global user_grid
    # Initialize a 2D array to store user inputs
    user_grid = [[0] * size for _ in range(size)]

    # Create validation function for entries
    vcmd = root.register(validate_entry)

    # Create new grid (frame to hold the grid entries, centered)
    grid_frame = tk.Frame(root, bg="#f4f6f9")
    # Place the grid frame and center it
    grid_frame.grid(row=1, column=0, columnspan=2, pady=20)
    grid_frame.grid_rowconfigure(0, weight=1)
    grid_frame.grid_columnconfigure(0, weight=1)

    # Create new grid entries
    for row in range(size):
        entry_row = []
        for col in range(size):
            entry = tk.Entry(grid_frame, width=3, justify='center', font=('Arial', 18), fg="black", bg="#f0f8ff",
                             highlightbackground="#b3cde0", highlightthickness=2, bd=0, relief='solid',
                             validate='key', validatecommand=(vcmd, '%P'))  # Input validation added here

            # If the cell is pre-filled, insert the value and disable the entry
            if pre_filled_grid[row][col] != 0:
                entry.insert(0, str(pre_filled_grid[row][col]))
                entry.config(state='disabled')  # Lock the pre-filled cell
                # Add pre-filled values to user_grid
                user_grid[row][col] = pre_filled_grid[row][col]
            else:
                entry.bind("<KeyRelease>",
                           lambda event, r=row, c=col, grid_size=size: validate_input(event, r, c, grid_size))

            # Add padding around each entry, making sure it's evenly spaced
            entry.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            entry_row.append(entry)

        # Add the row of entries to the global entries list
        entries.append(entry_row)

    # Adjust grid to be centered and take up the entire space
    for i in range(size):
        grid_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        grid_frame.grid_rowconfigure(i, weight=1, uniform="equal")


def validate_input(event, row, col, grid_size):
    input_value = event.widget.get()

    # Handle backspace or empty input gracefully
    if input_value == "":
        # Reset color to default when cleared
        event.widget.config(bg="#f0f8ff")
        user_grid[row][col] = 0  # Reset the grid cell to 0
        return

    event.widget.config(
        bg="#f0f8ff", highlightbackground="white", highlightthickness=1)

    if not input_value.isdigit() or int(input_value) > grid_size or int(input_value) < 1:
        event.widget.delete(0, tk.END)
        # Change the background color for invalid input
        event.widget.config(bg="orange", fg="black")
        messagebox.showerror(
            "Invalid Input", f"Please enter a number between 1 and {grid_size}.")
    else:
        # Update the user_grid with the input value if valid
        user_grid[row][col] = int(input_value)
        # Reset to default background color if valid
        event.widget.config(bg="light pink")

        # Check if all cells are filled
        if all(all(cell != 0 for cell in row) for row in user_grid):
            check_solution()  # Check the solution once the grid is fully filled


def solve_sudoku():
    """
    Solve the Sudoku puzzle using the selected method and update the grid with the solution.
    Displays solving time only if the puzzle is successfully solved.
    """
    current_level = level.get()  # Get the current difficulty level
    method = solving_method.get()  # Get the selected solving method

    # Check if Minimax is selected and the level is 2 or 3 (for 6x6 or larger puzzles)
    if method == "Minimax" and (current_level == 'LEVEL 2' or current_level == 'LEVEL 3'):
        messagebox.showinfo("Minimax Not Suitable",
                            "Minimax cannot solve THIS Sudoku puzzle. Please select a different solving method.")
        return

    # Reset and start timer for AI solving
    global start_time
    start_time = time.time()

    # Ensure a method is selected
    if not method:
        messagebox.showinfo("Select Method", "Please select a solving method.")
        return
    if current_level == 'LEVEL 1':
        max_num = 3  # For 3x3 grid, use numbers 1 to 3
    elif current_level == 'LEVEL 2':
        max_num = 6  # For 6x6 grid, use numbers 1 to 6
    elif current_level == 'LEVEL 3':
        max_num = 9  # For 9x9 grid, use numbers 1 to 9
    else:
        messagebox.showinfo("Error", "Invalid level selected.")
        return
    # Solve based on the selected method
    solution_found = False
    if method == "DFS":
        solution_found = dfs_solve(user_grid)
    elif method == "BFS":
        solution_found = bfs_solve(user_grid)
    elif method == "A*":
        solution_found = a_star_solve(user_grid)
    elif method == "CSP Backtracking":
        solution_found = backtracking_solve(user_grid, max_num)
    elif method == "Minimax":
        solution_found = minimax_solve(user_grid)
    else:
        messagebox.showinfo("Error", "Invalid solving method selected.")
        return

    # Update grid or display no solution message
    if solution_found:
        update_grid_with_solution()
        # Calculate and display solving time
        solving_time = time.time() - start_time
        messagebox.showinfo(
            "Solving Time", f"Solved in {solving_time:.2f} seconds")
    else:
        messagebox.showinfo(
            "No Solution", "The Sudoku puzzle cannot be solved.")

    # Clear entries and reload the level grid
    entries.clear()
    choose_level(current_level)

# Hint functionality


def provide_hint():
    global hints_used

    if hints_used >= hint_limit:
        messagebox.showinfo(
            "Hint Limit", f"No more hints available! You can use {hint_limit} hints in this level.")
        return

    empty_cells = [(r, c) for r in range(len(user_grid))
                   for c in range(len(user_grid[r])) if user_grid[r][c] == 0]
    if not empty_cells:
        messagebox.showinfo(
            "Puzzle Solved", "There are no empty cells to provide a hint.")
        return

    row, col = random.choice(empty_cells)
    user_grid[row][col] = solved_grid[row][col]
    entries[row][col].delete(0, tk.END)
    entries[row][col].insert(0, str(solved_grid[row][col]))
    # Highlight the hinted cell
    entries[row][col].config(state='disabled', bg="light blue")
    hints_used += 1


def choose_level(event):
    global solved_grid, hint_limit, hints_used, start_time, level

    hints_used = 0  # Reset hints used when changing level
    start_time = None  # Reset the timer when switching levels

    selected_level = level.get()

    if selected_level == "LEVEL 1":
        # Start the timer when a level is selected
        start_timer()
        hint_limit = 3
        pre_filled_grid = [
            [0, 3, 0],
            [2, 1, 0],
            [0, 0, 1]
        ]
        solved_grid = [
            [1, 3, 2],
            [2, 1, 3],
            [3, 2, 1]
        ]
        create_grid(3, pre_filled_grid)

    elif selected_level == "LEVEL 2":
        # Start the timer when a level is selected
        start_timer()
        hint_limit = 2
        pre_filled_grid = [
            [0, 0, 1, 0, 0, 4],
            [0, 5, 0, 0, 6, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [4, 0, 0, 0, 2, 0],
            [1, 0, 0, 0, 0, 0]
        ]
        solved_grid = [
            [6, 2, 1, 3, 5, 4],
            [3, 5, 4, 1, 6, 2],
            [5, 1, 3, 6, 4, 2],
            [2, 4, 6, 5, 3, 1],
            [4, 3, 5, 2, 1, 6],
            [1, 6, 2, 4, 5, 3]
        ]
        create_grid(6, pre_filled_grid)

    elif selected_level == "LEVEL 3":
        # Start the timer when a level is selected
        start_timer()
        hint_limit = 1
        pre_filled_grid = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        solved_grid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
        create_grid(9, pre_filled_grid)


def check_solution():
    """Check if the user's solution matches the solved grid."""
    for row in range(len(user_grid)):
        for col in range(len(user_grid[row])):
            if user_grid[row][col] != solved_grid[row][col]:
                messagebox.showerror(
                    "Incorrect Solution", "The solution is incorrect. Please try again!")
                return False
    messagebox.showinfo("Correct Solution",
                        "Congratulations! You've solved the puzzle correctly.")
    calculate_score()
    return True


def update_timer():
    """Update the timer label with the elapsed time."""
    global start_time
    if start_time is not None:
        elapsed_time = int(time.time() - start_time)
        timer_label.config(text=f"Time: {elapsed_time}s")
        root.after(1000, update_timer)


def start_timer():
    """Start the timer when the game begins."""
    global start_time
    start_time = time.time()
    update_timer()


def reset_game():
    """Reset the game state and timer."""
    global hints_used, start_time
    hints_used = 0
    start_time = None  # Reset start_time here
    for entry_row in entries:
        for entry in entry_row:
            entry.destroy()
    entries.clear()
    user_grid.clear()
    timer_label.config(text="Time: 0s")
    level.set("Choose Level")  # Reset the level selection to default state
    # Reset solving method selection
    solving_method.set("Select Solving Method")


def calculate_score():
    """Calculate and display the score based on hints used and time taken."""
    elapsed_time = int(time.time() - start_time)  # Total time taken in seconds
    base_score = 100  # Starting score
    hints_penalty = hints_used * 10  # Deduct 10 points for each hint used
    time_penalty = elapsed_time // 5  # Deduct 1 point for every 5 seconds taken

    # Calculate final score
    score = base_score - hints_penalty - time_penalty

    # Ensure score doesn't go below zero
    score = max(0, score)

    # Display the score
    messagebox.showinfo("Score", f"Your score: {score}")
    print(f"Your score is: {score}")  # Display or store the score as needed


def submit_solution():
    # Call this function when the user submits their solution
    check_solution()


# ----------------------------------------------------------------

def center_window(root, width, height):
    """Function to center the Tkinter window on the screen."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y coordinates to center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Set the geometry of the window with the calculated position
    root.geometry(f'{width}x{height}+{x}+{y}')


def game_screen():
    global level, solve_btn, timer_label, hint_btn, reset_btn, submit_button, clear_button, root, solving_method

    root = tk.Tk()
    root.title("Sudoku Solver")
    if (level.get() == "LEVEL 1"):
        root.geometry("410x380")
        center_window(root, 410, 380)

    elif (level.get() == "LEVEL 2"):
        root.geometry("410x500")
        center_window(root, 410, 500)

    else:
        root.geometry("510x620")  # Window size
        center_window(root, 510, 620)
    root.configure(bg="#f4f6f9")  # Background color

    # row 1

    current_level = tk.Label(root, text=level.get(), font=(
        'Arial', 12), bg="#f4f6f9")
    current_level.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # Timer label
    timer_label = tk.Label(root, text="Time: 0s",
                           font=('Arial', 12), bg="#f4f6f9")
    timer_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    # row 2
    # handled in create_grid

    # row 3
    button_frame = tk.Frame(root, bg="#f4f6f9")
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)
    # Solve button
    solve_btn = tk.Button(button_frame, text="Solve", command=solve_sudoku, font=(
        'Arial', 13), bg="dark blue", fg="white", width=8)
    solve_btn.grid(row=0, column=3, padx=10, pady=5)

    # Hint button
    hint_btn = tk.Button(button_frame, text="Hint", command=provide_hint, font=(
        'Arial', 13), bg="purple", fg="white", width=8)
    hint_btn.grid(row=0, column=1, padx=10, pady=5)

    # Reset button
    reset_btn = tk.Button(button_frame, text="Reset", command=reset_game, font=(
        'Arial', 13), bg="#e61919", fg="white", width=8)
    reset_btn.grid(row=0, column=2, padx=10, pady=5)

    # Submit button
    submit_button = tk.Button(button_frame, text="Submit", command=check_solution, font=(
        'Arial', 13), bg="#037ffc", fg="white", width=8)
    submit_button.grid(row=0, column=0, padx=10, pady=5)

    # Create label
    label1 = tk.Label(root, text="Click 'CLEAR GRID' to solve \n through a method if you've entered any numbers .", font=(
        'Arial', 10), bg="#f4f6f9")
    label1.grid(row=3, column=0, columnspan=2, padx=10, pady=0)

    def clear_grid():
        current_level = level.get()  # Get the current difficulty level
        entries.clear()
        choose_level(current_level)

    # Clear grid button
    clear_button = tk.Button(root, text="Clear Grid", command=clear_grid, font=(
        'Arial', 13), bg="#3aa0c2", fg="white", width=8)
    clear_button.grid(row=4, column=0, columnspan=2, pady=4)

    choose_level(level.get())

    root.mainloop()


def change_window(root):
    """Destroys the current window (root) and calls the game_screen function."""
    root.destroy()  # Destroy the current root window
    game_screen()  # Call the game_screen function to open the game window


def main():

    global level, root, solving_method
    root = tk.Tk()
    root.title("Sudoku Solver")
    root.geometry("400x300")  # Window size
    root.configure(bg="#f4f6f9")  # Lighter background color for a modern look
    center_window(root, 400, 300)

    # Create the welcome label and center it with improved font and styling
    welcome_label = tk.Label(root, text="Welcome to Sudoku Solver", font=(
        'Poppins', 20, 'bold'), fg="#2e3b4e", bg="#f4f6f9")
    welcome_label.grid(row=0, column=0, pady=20, padx=20, sticky="n")

    # Level selection dropdown with enhanced styling
    level = tk.StringVar()
    level.set("Choose Level")
    levels = tk.OptionMenu(root, level, "LEVEL 1",
                           "LEVEL 2", "LEVEL 3")
    levels.grid(row=1, column=0, pady=10, padx=20, sticky="n")
    levels.configure(bg="#dbe9f4", fg="#2e3b4e", font=(
        'Poppins', 13), relief="flat", width=18)

    # Solving method selection dropdown with better visual style

    solving_method = tk.StringVar()
    solving_method.set("Select Solving Method")  # Default option
    solving_methods = tk.OptionMenu(
        root, solving_method, "DFS", "A*", "BFS", "CSP Backtracking", "Minimax")
    solving_methods.grid(row=2, column=0, pady=10, padx=20, sticky="n")
    solving_methods.configure(bg="#dbe9f4", fg="#2e3b4e", font=(
        'Poppins', 13), relief="flat", width=18)

    # Play button with improved design
    play_button = tk.Button(root, text="Play", command=lambda: change_window(root), font=('Poppins', 13, 'bold'),
                            bg="#037ffc", fg="white", width=8, relief="raised", bd=2)
    play_button.grid(row=3, column=0, pady=20, padx=20, sticky="n")
    play_button.config(activebackground="#186fc7",
                       activeforeground="white")  # Button hover effect

    # Configure rows and columns for center alignment
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)

    root.grid_columnconfigure(0, weight=1)  # Center the column

    # Run the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()
