import datetime as dt

from cassia import entries, config, lexing
from cassia import actions

from subprocess import run


import questionary

# TODO print n
# TODO print last entry datetime (George needs to see most recent date)
# TODO Edit the log in vim

# Greet User
print("Welcome to CASSIA!\n")
# print recent entries
actions.print_recent()
while True:
    # Prompt input
    option = questionary.text("New Entry [%H%M + description], [R]eports, [D]elete last, [L]ist, [P]rint, e[X]it:",
                              lexer=lexing.SelectActionLexer(), style=lexing.select_action_style).ask()
    # Input parsing for exit
    if option.upper() in ['L', 'LIST']:
        field = questionary.select("List:" , choices=['categories', 'subcategories', 'descriptions']).ask()
        actions.list(field)
    elif option.upper() in ['X', 'EXIT', 'QUIT', 'Q']:
        break
    elif option.upper() in ['D', 'DELETE']:
        actions.delete()
    elif option.upper() in ['R', 'REPORTS']:
        actions.reports()
    elif option.upper() in ['P', 'PRINT']:
        actions.print_recent()
    elif actions.parse_option_time(option):
        actions.create(option)
    else:
        run(['vim','/tmp/cassia.log'])
        print("Try again!")