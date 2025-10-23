import csv # Lets the program read .csv files that contain Sudoku puzzles.
import tkinter as tk # The built-in GUI library
import time # Used to measure how long solving takes (approx.)

from tkinter import filedialog, messagebox

# --------------------------------------------------------------------------
# Solver (bitset + Minimum Remaining Values + forward checking) 
# --------------------------------------------------------------------------

FULL = 0b111111111 # Each bit has the potential to represent digits 1-9, logic: switching lights ON or OFF
# EXAMPLE : 0b000010000 means only 5 can go in that cell (5th bit from right is ON)
N = 9 # Number of rows / columns
size = N * N # Number of cells

# The method we have used manipulates bits heavily, that is the usage of 0's and 1's 

# Starting with an empty array to hold each cell's "peers", that is, the other cells it must check against
# Same row, same column, same box
PEERS = []

# Each cell has up to 20 peers (8 in row + 8 in column + 4 in box, minus overlaps)
# Hint (Visualizing it): 
# Consider cell X and it's peers Y
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | 0 Y 0 | 0 0 0
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | 0 Y 0 | 0 0 0
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | 0 Y 0 | 0 0 0
# ---------------------             ---------------------
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | Y Y Y | 0 0 0
# 0 0 0 | 0 X 0 | 0 0 0    ---->    Y Y Y | Y X Y | Y Y Y 
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | Y Y Y | 0 0 0
# ---------------------             ---------------------
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | 0 Y 0 | 0 0 0
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | 0 Y 0 | 0 0 0
# 0 0 0 | 0 0 0 | 0 0 0             0 0 0 | 0 Y 0 | 0 0 0

for index in range(size):
    current_row = index // 9
    current_column = index % 9
    box_row_start = (current_row // 3) * 3
    box_column_start = (current_column // 3) * 3

    # All cells in the same row
    same_row = {current_row * 9 + c for c in range(9)}

    # All cells in the same column
    same_col = {r * 9 + current_column for r in range(9)}

    # All cells in the same 3x3 box
    same_box = set()
    for r_offset in range(3):
        for c_offset in range(3):
            cell_index = (box_row_start + r_offset) * 9 + (box_column_start + c_offset)
            same_box.add(cell_index)

    # Combine all peers, from Set Theory, | represents the Union function
    all_peers = same_row | same_col | same_box
    all_peers.discard(index) # Removing the cell itself from its peers
    PEERS.append(tuple(all_peers)) # Adding the tuple of peers of current cell to the PEERS list

# Initialize the list of possible numbers (candidates) for each Sudoku cell.
def init_candidates(grid):

    # Starting by assuming all digits (1–9) are possible for every cell, and so, we need 9x9=81 numbers
    candidates = [FULL]*size
    
    # Going through each of the 81 cells one by one
    for cell_index in range(size):

        # This is the value at that particular row and column
        value = grid[cell_index]

        # If the cell is already filled in the puzzle, that is if it has been allotted from 1-9
        if value != 0:
            # Converting the value into a bitmask, by shifting 1 into correct position
            # ex: to denote 5 → 0b000010000, that is 5th number from the right is turned on
            # and for this it should be shifted from (5-1) = 4 shifts from the right
            bitmask = 1 << (value - 1)

            # Locking this cell’s candidates to that number
            candidates[cell_index] = bitmask

            # Now, we are removing this number from all its peers (same row, col, or box)
            for peer_index in PEERS[cell_index]:
                # Using bitwise AND and NOT to clear that bit
                # Example: if bitmask = 0b000010000,
                # then ~bitmask = 0b111101111 (so we are actually “turning off” the 5 from peers)
                candidates[peer_index] &= ~bitmask

    # Returning the final candidates list (each entry is a 9-bit mask)
    return candidates

# MRV - Minimum Remaining Value Heuristics
# This function chooses the next cell to fill in Sudoku using the MRV principle.
# Helps reduce branching in the search tree and makes solving faster.
def choose_next_cell(candidates):
    
    fewest_options = 10    # start larger than any possible count (max = 9)
    chosen_index = -1      # default if all cells are solved

    # Goes through all 81 cells
    for cell_index in range(size):
        possibilities = candidates[cell_index].bit_count() # count the number of 1's present in value

        # Skip solved cells (exactly one possibility)
        # Also skip cells that have more possibilities than the current minimum
        if 1 < possibilities < fewest_options:
            # updating the fewest options with possibilities
            # this cell has fewer options than any previous one
            fewest_options = possibilities
            chosen_index = cell_index

            # 2 possibilities is already very constrained so break out of loop 
            if fewest_options == 2:
                break

    #Return the index (0–80) of the most constrained unsolved cell or -1 if every cell is already filled.
    return chosen_index

def propagate_value(candidates, cell_index, value_mask):
    
    # Fixing this cell's candidates to only the chosen value.
    candidates[cell_index] = value_mask

    # Updating all peers (cells in the same row, column, or box)
    for peer_index in PEERS[cell_index]:
        
        # Checking if the peer currently allows this number (bit overlap)
        if candidates[peer_index] & value_mask:
            
            # Removing that number from the peer's candidate list
            # Using bitwise AND with NOT (~value_mask)
            # That is if value_mask = 0b000010000 (number 5) then ~value_mask = 0b111101111 → turns off 
            # that bit for all it's peers
            candidates[peer_index] &= ~value_mask

            # If the peer now has no possible values then the current placement has made the puzzle invalid and we need to backtrack
            if candidates[peer_index] == 0:
                return False

            # If the peer now has exactly one possible value left, assign it recursively to continue propagation.
            # The condition (x & (x - 1)) == 0 checks if only one bit is set.
            # Ex: candidates[52] = 0b000100000 AND candidates[52] - 1 = 0b000011111 gives 0b000000000
            if candidates[peer_index] & (candidates[peer_index] - 1) == 0:
                # if propagation fails, immediately stop and signal backtracking
                if not propagate_value(candidates, peer_index, candidates[peer_index]):
                    return False

    # If no contradictions occurred, the assignment is consistent.
    return True

# Depth-First Search Sudoku Solver 
def solve_with_dfs(candidates, grid, entries, stats, root, original_cells):
    # Checking if every cell is solved (1 bit per cell)
    puzzle_solved = True

    # For all masked values in candidates
    for mask in candidates:
        # (mask & (mask - 1)) == 0 means exactly one bit is ON
        if mask & (mask - 1) != 0:
            puzzle_solved = False
            break

    # If every cell was solved, fill grid with final numbers
    if puzzle_solved:
        for i in range(size):
            grid[i] = candidates[i].bit_length() # how many places to shift left to reach the ‘1’ bit.
            # Update the GUI with correct colors for final solution
            row = i // 9
            col = i % 9
            if not original_cells[row][col]:  # Only color non-original cells blue
                entries[row][col].delete(0, tk.END)
                entries[row][col].insert(0, str(grid[i]))
                entries[row][col].config(fg='blue')
        return True

    # Picking the next most constrained cell (MRV)
    pos = choose_next_cell(candidates)
    if pos == -1:
        return False  # no available cell

    row = pos // 9   # integer division for which row (0–8)
    col = pos % 9    # remainder for which column (0–8)

    # Listing all possible digits (bit options)
    options = []
    for d in range(9):
        bit = 1 << d # d moves from 0-8
        # basically AND's and checks whether that value
        if candidates[pos] & bit:
            options.append(bit)

    # Try assigning each possible number
    for bitmask in options:
        # Copy the current candidate state, without destroying any previous state
        cand_copy = candidates[:]

        # Try to assign and propagate the chosen number
        if propagate_value(cand_copy, pos, bitmask):
            stats['steps'] += 1
            grid[pos] = bitmask.bit_length()  # convert bitmask → digit (1–9)
            # Update GUI
            entries[row][col].delete(0, tk.END)
            entries[row][col].insert(0, str(grid[pos]))
            entries[row][col].config(fg='blue')
            root.update()
            root.after(10)

            # Recursively going deeper
            if solve_with_dfs(cand_copy, grid, entries, stats, root, original_cells):
                candidates[:] = cand_copy
                return True  # solved the puzzle completely
            
        stats['backtracks'] += 1
        grid[pos] = 0
        
       # Update GUI to remove the number (backtrack)
        root.update()
        root.after(10)
        
    # No number worked then dead end so return False
    return False

# GUI code separated below

def read_sudoku_from_csv(file_path):
    # reads a sudoku puzzle from a csv file and returns it as a 2D list
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        puzzle = []
        for row in reader:
            puzzle.append([int(cell) if cell.strip() else 0 for cell in row])
    return puzzle


def display_sudoku():
    root = tk.Tk()
    root.title("Sudoku Solver - Bitset + MRV + Forward Checking")
    
    # Start with an empty grid
    grid = [[0]*9 for _ in range(9)]
    
    # Track original cells - initialize all as False
    original_cells = [[False]*9 for _ in range(9)]

   
    # Display information that original = black and solved = blue
    info_label = tk.Label(root, text="Original: Black, Solved: Blue", 
                         font=('Arial', 14))
    info_label.pack(pady=5)
    
    # Create main frame
    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10)
    
    # Create a frame for the Sudoku grid with thicker border
    grid_frame = tk.Frame(main_frame, borderwidth=1, relief='solid', bg='black')
    grid_frame.pack(pady=10)
    
    # create 3x3 subgrid frames
    subgrid_frames = []
    for box_i in range(3):
        row_frames = []
        for box_j in range(3):
            # give each subgrid a border
            subgrid_frame = tk.Frame(grid_frame, borderwidth=1, relief='solid', bg='black')
            subgrid_frame.grid(row=box_i, column=box_j, padx=1, pady=1)
            row_frames.append(subgrid_frame)
        subgrid_frames.append(row_frames)
        
    # Create Entry widgets for each cell in the grid
    entries = []     
    for i in range(9):
        row_entries = []
        for j in range(9):
            value = grid[i][j]
            cell_value = '' if value == 0 else str(value) 
            
            subgrid_i = i // 3
            subgrid_j = j // 3
            cell_i = i % 3
            cell_j = j % 3
            subgrid_frame = subgrid_frames[subgrid_i][subgrid_j]
            
            # Create Entry widget for each cell
            entry = tk.Entry(subgrid_frame, width=3, justify="center",
                            font=('Arial', 18), bg='white', fg='black',
                            borderwidth=1, relief='solid')
            entry.insert(0, cell_value)
            entry.grid(row=cell_i, column=cell_j, padx=1, pady=1, ipadx=5, ipady=5)
            row_entries.append(entry)
        entries.append(row_entries)
        
    stats = {
        'steps': 0,
        'backtracks': 0
    }
    
    # Create stats frame below the grid
    stats_frame = tk.Frame(main_frame)
    stats_frame.pack(pady=10)
            
    # Create stats labels below the grid
    time_label = tk.Label(stats_frame, text="Time: Click Start to Solve", font=('Arial', 12))
    time_label.grid(row=9, column=0, columnspan=9, pady=10)
    
    steps_label = tk.Label(stats_frame, text="Steps: 0", font=('Arial', 12))
    steps_label.grid(row=10, column=0, columnspan=9, pady=5)
    
    backtracks_label = tk.Label(stats_frame, text="Backtracks: 0", font=('Arial', 12))
    backtracks_label.grid(row=11, column=0, columnspan=9, pady=5)
    
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
        
    def start_solving():
        # Hide start button and show reset button
        start_button.pack_forget()
        reset_button.pack(side='left', padx=10)
        # Read current values from entries
        for i in range(9):
            for j in range(9):
                value = entries[i][j].get().strip()
                grid[i][j] = int(value) if value.isdigit() and 1 <= int(value) <= 9 else 0
        # Convert 2D grid to 1D for the bitset solver
        flat_grid = []
        for i in range(9):
            for j in range(9):
                flat_grid.append(grid[i][j])
        
        stats['steps'] = 0
        stats['backtracks'] = 0
        start_time = time.time()
        
        # Initialize candidates and solve using the bitset solver
        candidates = init_candidates(flat_grid[:])
        
        # Call the DFS solver
        solve_with_dfs(candidates, flat_grid, entries, stats, root, original_cells)
        
        # Convert back to 2D grid for display
        for i in range(9):
            for j in range(9):
                grid[i][j] = flat_grid[i * 9 + j] 
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Update final display
        for i in range(9):
            for j in range(9):
                entries[i][j].delete(0, tk.END) # Clear existing entry to prevent user input from mixing with the solution
                if grid[i][j] != 0:
                    entries[i][j].insert(0, str(grid[i][j])) # Insert solved value
        
        # Update stats
        time_label.config(text=f"Total Execution Time: {total_time:.2f} seconds")
        steps_label.config(text=f"Total Steps: {stats['steps']}")
        backtracks_label.config(text=f"Total Backtracks: {stats['backtracks']}")
        
    def initialise_puzzle(puzzle):
        grid.clear()
        # Load the puzzle into the grid
        for row in puzzle:
            grid.append([cell for cell in row])
            
        for i in range(9):
            for j in range(9):
                value = grid[i][j] 
                entries[i][j].delete(0, tk.END) # Clear existing entry, may be from previous puzzle or user input
                if value != 0:
                    entries[i][j].insert(0, str(value)) # Insert the puzzle value in the respective cell
                entries[i][j].config(fg='black') 
        
        reset_button.pack_forget()
        start_button.pack(side='left', padx=10)
        
        stats['steps'] = 0
        stats['backtracks'] = 0
        steps_label.config(text="Steps: 0")
        backtracks_label.config(text="Backtracks: 0")
        time_label.config(text="Time: Click Start to Solve")
        
    def load_file(): 
        # Open file dialog to select a CSV file
        f = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not f: # User cancelled file dialog
            return
        try:
            puzzle = read_sudoku_from_csv(f) # Read the puzzle from the selected file
            if len(puzzle) != 9: # Validate the puzzle format
                messagebox.showerror("Error", "Invalid Sudoku format - must have 9 rows")
                return
            for row in puzzle:
                if len(row) != 9: # Validate each row
                    messagebox.showerror("Error", "Invalid Sudoku format - each row must have 9 columns")
                    return
                
            # Set which cells are originally filled
            for i in range(9):
                for j in range(9):
                    original_cells[i][j] = (puzzle[i][j] != 0) # True if original cell, False otherwise
            initialise_puzzle(puzzle) # Initialize the puzzle in the GUI
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            
    def reset_puzzle():
        # Hide reset button and show start button
        reset_button.pack_forget()
        start_button.pack(side='left', padx=10)
        
        # Reload the original puzzle state
        for i in range(9):
            for j in range(9):
                if original_cells[i][j]:  # If it was an original cell
                    entries[i][j].delete(0, tk.END) # Clear existing entry
                    entries[i][j].insert(0, str(grid[i][j])) # Reinsert original value
                    entries[i][j].config(fg='black')
                else:  # If it was filled during solving
                    grid[i][j] = 0
                    entries[i][j].delete(0, tk.END) # Clear the cell
        
        stats['steps'] = 0
        stats['backtracks'] = 0
        steps_label.config(text="Steps: 0")
        backtracks_label.config(text="Backtracks: 0")
        time_label.config(text="Time: Click Start to Solve")
    
    # Load file button
    load_button = tk.Button(button_frame, text="Load File", command=load_file, font=('Arial', 12))
    load_button.pack(side='left', padx=10)

    # Start button
    start_button = tk.Button(button_frame, text="Start Solving", command=start_solving, font=('Arial', 12))   
    start_button.pack(side='left', padx=10)

    # Reset button
    reset_button = tk.Button(button_frame, text="Reset Puzzle", command=reset_puzzle, font=('Arial', 12))
    reset_button.pack(side='left', padx=10)
    reset_button.pack_forget()  # Hide reset button initially
    
    root.mainloop()

display_sudoku()



