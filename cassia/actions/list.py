from cassia import entries
import shutil
def list(field):
    if field == 'categories':
        print_grid(entries.list_field('category'))
    elif field == 'subcategories':
        print_grid(entries.list_field('subcategory'))
    elif field == 'descriptions':
        print_grid(entries.list_field('description', limit=15))

def print_grid(words: list):
    # get the max width of the words
    max_width = max([len(word) for word in words])
    # get the width of the terminal
    terminal_width = shutil.get_terminal_size().columns
    # calculate the number of columns
    num_columns = min((terminal_width // (max_width + 4)), 3)
    # calculate the number of rows
    num_rows = (len(words) // num_columns) + 1
    # print the words in a grid
    for i in range(num_rows):
        for j in range(num_columns):
            index = i + j*num_rows
            if index < len(words):
                print(f"{words[index]:<{max_width+4}}", end='')
        print()