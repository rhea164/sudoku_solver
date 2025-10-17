import csv
import tkinter as tk
import time

def read_sudoku_from_csv(file_path):
    """Reads a Sudoku puzzle from a CSV file and returns it as a 2D list."""
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        puzzle = []
        for row in reader:
            puzzle.append([int(cell) if cell.strip() else 0 for cell in row])
    return puzzle


    
def is_valid_placement(num, grid, row, col):
    # Check row
    for j in range(9):
        if grid[row][j]==num:
            return False
    # Check column
    for i in range(9):
        if grid[i][col]==num:
            return False
    # Check 3x3 box
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for i in range(box_row_start, box_row_start + 3):
        for j in range(box_col_start, box_col_start + 3):
            if grid[i][j]==num:
                return False
    return True
    

def problem_empty_cell(grid, row, col, value):
    # temporarily place the value in the cell
    grid[row][col] = value
    
    for j in range(9):
        if grid[row][j]==0:
            has_option=False
            for test_num in range(1,10):
                if is_valid_placement(test_num,grid,row,j):
                    has_option=True
                    break
            if not has_option:
                grid[row][col]=0
                return True
    
    for i in range(9):
        if grid[i][col]==0:
            has_option=False
            for test_num in range(1,10):
                if is_valid_placement(test_num,grid,i,col):
                    has_option=True
                    break
            if not has_option:
                grid[row][col]=0
                return True
            
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for i in range(box_row_start, box_row_start + 3):   
        for j in range(box_col_start, box_col_start + 3):
            if grid[i][j]==0:
                has_option=False
                for test_num in range(1,10):
                    if is_valid_placement(test_num,grid,i,j):
                        has_option=True
                        break
                if not has_option:
                    grid[row][col]=0
                    return True
                
    # after checking the temporary placement and finding no problems, remove the temporary placement
    grid[row][col]=0
    # no problems found so return false
    return False


def find_empty_cell(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)  # row, col
    return None

        
def solve_sudoku(grid, labels, stats, root):
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True
    row, col = empty_cell
    
    for num in range(1,10):
        if is_valid_placement(num,grid,row,col):
            if not problem_empty_cell(grid,row,col,num):
                grid[row][col]=num
                stats['steps'] += 1
                labels[row][col].config(text=str(num), fg='blue')
                root.update()
                root.after(10) 
                # update_counter[0] += 1
                
                # Update every 10 moves
                # if update_counter[0] % 10 == 0:
                #     for i in range(9):
                #         for j in range(9):
                #             labels[i][j].config(text=str(grid[i][j]) if grid[i][j] != 0 else '')
                #     root.update()
                
                if solve_sudoku(grid,labels,stats, root):
                    return True
                
                grid[row][col]=0
                stats['backtracks'] += 1
                labels[row][col].config(text='')
                root.update()
                root.after(10) 
                
                # update_counter[0] += 1
                
                # Update every 10 moves during backtrack too
                # if update_counter[0] % 10 == 0:
                #     for i in range(9):
                #         for j in range(9):
                #             labels[i][j].config(text=str(grid[i][j]) if grid[i][j] != 0 else '')
                #     root.update()
    
    return False


    

def display_sudoku():
    root = tk.Tk()
    root.title("Sudoku Solver")
    
    default_puzzle = read_sudoku_from_csv('sudoku_medium.csv')
    grid = []
    for row in default_puzzle:
        grid.append([cell for cell in row])

    
    # Create difficulty selection frame
    diff_frame=tk.Frame(root)
    diff_frame.pack(pady=5)
    
    tk.Label(diff_frame, text="Select Difficulty:",font=('Arial', 12)).pack(side='left', padx=5)
    difficulty=tk.StringVar(value='Medium')
    
    def load_difficulty():
        level=difficulty.get()
        if level=='Easy':
            puzzle=read_sudoku_from_csv('sudoku_easy.csv')
        elif level=='Medium':
            puzzle=read_sudoku_from_csv('sudoku_medium.csv')
        elif level=='Hard':
            puzzle=read_sudoku_from_csv('sudoku_hard.csv')
        
        initialise_puzzle(puzzle)
        
    tk.Radiobutton(diff_frame, text="Easy", variable=difficulty, value='Easy', command=load_difficulty,font=('Arial', 12)).pack(side='left', padx=5)
    tk.Radiobutton(diff_frame, text="Medium", variable=difficulty, value='Medium', command=load_difficulty,font=('Arial', 12)).pack(side='left', padx=5)
    tk.Radiobutton(diff_frame, text="Hard", variable=difficulty, value='Hard', command=load_difficulty,font=('Arial', 12)).pack(side='left', padx=5)
    
    
    #display the information that original = black and solved = blue
    info_label = tk.Label(root, text="Original : Black, Solved : Blue", font=('Arial', 14))
    info_label.pack(pady=5)
    
    # Create main frame
    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10)
    
    # Create a frame for the Sudoku grid with thicker border
    grid_frame = tk.Frame(main_frame, borderwidth=1, relief='solid', bg='black')
    grid_frame.pack(pady=10)
    
    subgrid_frames = []
    for box_i in range(3):
        row_frames = []
        for box_j in range(3):
            subgrid_frame = tk.Frame(grid_frame, borderwidth=1, relief='solid', bg='black')
            subgrid_frame.grid(row=box_i, column=box_j, padx=1, pady=1)
            row_frames.append(subgrid_frame)
        subgrid_frames.append(row_frames)
        
    labels=[]    
    for i in range(9):
        row_labels = []
        for j in range(9):
            value = grid[i][j]
            cell_value = '' if value == 0 else str(value)
            
            subgrid_i = i // 3
            subgrid_j = j // 3
            cell_i = i % 3
            cell_j = j % 3
            subgrid_frame = subgrid_frames[subgrid_i][subgrid_j]
            label = tk.Label(subgrid_frame, text=cell_value, width=4, height=2, font=('Arial', 18),bg='white', fg='black')
            label.grid(row=cell_i, column=cell_j, padx=1, pady=1)
            row_labels.append(label)
        labels.append(row_labels)
        
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
        stats['steps'] = 0
        stats['backtracks'] = 0
        start_time = time.time()
            
        # Call the solver 
        solve_sudoku(grid, labels, stats, root)
        
        end_time = time.time()
        total_time = end_time - start_time
        # update time label with total time
        time_label.config(text=f"Total Execution Time: {total_time:.2f} seconds")
        steps_label.config(text=f"Total Steps: {stats['steps']}")
        backtracks_label.config(text=f"Total Backtracks: {stats['backtracks']}")
        
    def initialise_puzzle(puzzle):
        grid.clear()
        for row in puzzle:
            grid.append([cell for cell in row])
            
        for i in range(9):
            for j in range(9):
                value=grid[i][j]
                labels[i][j].config(text=str(value) if value!=0 else '', fg='black')
        stats['steps'] = 0
        stats['backtracks'] = 0
        steps_label.config(text="Steps: 0")
        backtracks_label.config(text="Backtracks: 0")
        time_label.config(text="Time: Click Start to Solve")
    
    def reset_puzzle(puzzle=None):
        if puzzle is None:
            level=difficulty.get()
            if level=='Easy':
                puzzle=read_sudoku_from_csv('sudoku_easy.csv')
            elif level=='Medium':
                puzzle=read_sudoku_from_csv('sudoku_medium.csv')
            elif level=='Hard':
                puzzle=read_sudoku_from_csv('sudoku_hard.csv')
        
        initialise_puzzle(puzzle)
        
    #start button
    start_button = tk.Button(button_frame, text="Start Solving", command=start_solving, font=('Arial', 12))   
    start_button.pack(side='left', padx=10)
    
    #reset button
    reset_button = tk.Button(button_frame, text="Reset Puzzle", command=reset_puzzle, font=('Arial', 12))
    reset_button.pack(side='left', padx=10)
    
        

    # After solving, update all labels to show the final solution
    # for i in range(9):
    #     for j in range(9):
    #         labels[i][j].config(text=str(grid[i][j]) if grid[i][j] != 0 else '', fg='black')
    # root.update()
    
    root.mainloop()
    
    
display_sudoku()

        