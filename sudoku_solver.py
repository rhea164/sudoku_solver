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

puzzle = read_sudoku_from_csv('sudoku3.csv')
for row in puzzle:
    print (row)
    
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
    
# def initialize_domains(grid):
#     domains=[]
#     for i in range(9):
#         row_domain=[]
#         for j in range(9):
#             domain = set()
#             if grid[i][j]!=0:
#                 domain.add(grid[i][j])
#             else:
#                 for num in range(1,10):
#                     if is_valid_placement(num,grid,i,j):
#                         domain.add(num)
#             row_domain.append(domain)
#         domains.append(row_domain)
#     return domains

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

        
def solve_sudoku(grid, labels, stats, root, update_counter=[0]):
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True
    row, col = empty_cell
    
    for num in range(1,10):
        if is_valid_placement(num,grid,row,col):
            if not problem_empty_cell(grid,row,col,num):
                grid[row][col]=num
                stats['steps'] += 1
                update_counter[0] += 1
                
                # Update every 10 moves
                if update_counter[0] % 10 == 0:
                    for i in range(9):
                        for j in range(9):
                            labels[i][j].config(text=str(grid[i][j]) if grid[i][j] != 0 else '')
                    root.update()
                
                if solve_sudoku(grid,labels,stats, root, update_counter):
                    return True
                
                grid[row][col]=0
                stats['backtracks'] += 1
                update_counter[0] += 1
                
                # Update every 10 moves during backtrack too
                if update_counter[0] % 10 == 0:
                    for i in range(9):
                        for j in range(9):
                            labels[i][j].config(text=str(grid[i][j]) if grid[i][j] != 0 else '')
                    root.update()
    
    return False

def display_sudoku(grid):
    root = tk.Tk()
    root.title("Sudoku Solver")
    labels = []
    for i in range(9):
        row=[]
        for j in range(9):
            row.append(None)
        labels.append(row)
    for i in range(9):
        for j in range(9):
            value = grid[i][j]
            cell_value ='' if value==0 else str(value)
            
            label = tk.Label(root, width=2, font=('Arial', 24), borderwidth=1,justify='center', text=cell_value, relief ='solid')
            label.grid(row=i, column=j, padx=5, pady=5)
            labels[i][j]= label
            
    # Create stats labels below the grid
    time_label = tk.Label(root, text="Time: Calculating...", font=('Arial', 12))
    time_label.grid(row=9, column=0, columnspan=9, pady=10)
    
    steps_label = tk.Label(root, text="Steps: 0", font=('Arial', 12))
    steps_label.grid(row=10, column=0, columnspan=9, pady=5)
    
    backtracks_label = tk.Label(root, text="Backtracks: 0", font=('Arial', 12))
    backtracks_label.grid(row=11, column=0, columnspan=9, pady=5)
    
    stats = {
        'steps': 0,
        'backtracks': 0
    }
        
    
    start_time = time.time()
            
      # Call the solver 
    solve_sudoku(grid, labels, stats, root)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # update time label with total time
    time_label.config(text=f"Total Execution Time: {total_time:.2f} seconds")
    steps_label.config(text=f"Total Steps: {stats['steps']}")
    backtracks_label.config(text=f"Total Backtracks: {stats['backtracks']}")
    
    # After solving, update all labels to show the final solution
    for i in range(9):
        for j in range(9):
            labels[i][j].config(text=str(grid[i][j]) if grid[i][j] != 0 else '', fg='black')
    root.update()
    
    root.mainloop()
    
display_sudoku(puzzle)

        