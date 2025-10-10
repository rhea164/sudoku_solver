import csv
import tkinter as tk

def read_sudoku_from_csv(file_path):
    """Reads a Sudoku puzzle from a CSV file and returns it as a 2D list."""
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        puzzle = []
        for row in reader:
            puzzle.append([int(cell) if cell.strip() else 0 for cell in row])
    return puzzle

puzzle = read_sudoku_from_csv('sudoku.csv')
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
    
def initialize_domains(grid):
    domains=[]
    for i in range(9):
        row_domain=[]
        for j in range(9):
            domain = set()
            if grid[i][j]!=0:
                domain.add(grid[i][j])
            else:
                for num in range(1,10):
                    if is_valid_placement(num,grid,i,j):
                        domain.add(num)
            row_domain.append(domain)
        domains.append(row_domain)
    return domains

def forward_checking(grid, row, col, value, domains):
    pruned=[]
    # Update the grid
    grid[row][col] = value
    # Update the domains of related cells
    for j in range(9):
        if j != col and value in domains[row][j]:
            domains[row][j].remove(value)
            pruned.append((row, j, value))
    for i in range(9):
        if i != row and value in domains[i][col]:
            domains[i][col].remove(value)
            pruned.append((i, col, value))
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for i in range(box_row_start, box_row_start + 3):
        for j in range(box_col_start, box_col_start + 3):
            if (i != row or j != col) and value in domains[i][j]:
                domains[i][j].remove(value)
                pruned.append((i, j, value))
    return pruned

domains = initialize_domains(puzzle)
print(domains[0][2]) 


def find_empty_cell(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)  # row, col
    return None

def restore_domains(domains, pruned):
    for (i, j, val) in pruned:
        domains[i][j].add(val)
        
def solve_sudoku(grid, domains, labels, root):
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True  # Solved
    row, col = empty_cell
    for value in list(domains[row][col]):
        if is_valid_placement(value, grid, row, col):
            pruned = forward_checking(grid, row, col, value, domains)
            labels[row][col].config(text=str(value), fg='blue')
            root.update()
            root.after(100)  # Pause for visual effect
            if solve_sudoku(grid, domains, labels, root):
                return True
            # Backtrack
            grid[row][col] = 0
            restore_domains(domains, pruned)
            labels[row][col].config(text='', fg='black')
            root.update()
            root.after(100)  # Pause for visual effect
    return False


# def get_domain(grid,row,col):
#     for i in range(1,10):
#         if is_valid_placement(i,grid,row,col):


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
    root.mainloop()
    
display_sudoku(puzzle)

        