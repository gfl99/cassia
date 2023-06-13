import datetime as dt
import time
import pandas as pd
from fuzzywuzzy import fuzz
from cassia import readwrite, analysis, config, tools
from cassia.tools import colors, YELLOW, GREEN, RED, DEFAULT_COLOR, BOLD, MAGENTA

def check_datetime_validity(string, format):
    try:
        return dt.datetime.strptime(string, format)
    except ValueError:
        return False

def console(logfile):
    # Greet User
    print("Hello!")
    while True:
        print_recent_entries()  # TODO
        # Print all entries from current day
        print("----------------------------------------")
        # Prompt input
        option = input(
            f"\n{YELLOW}Options: New Entry [%H%M + description], [R]eports, [D]elete last line, [L]ist cat/sub/desc,  e[X]it: {DEFAULT_COLOR}")
        # Input parsing for exit
        if option.upper() in ['L', 'LIST']:
            field = tools.prompt_hotkeys("field", ['category', 'subcategory', 'description'], allow_new=False)
            print(analysis.list_unique_values(df, field))
        elif option.upper() in ['X', 'EXIT', 'QUIT']:
            break
        elif option.upper() in ['D', 'DELETE']:
            working_datetime = readwrite.delete_last_entry()
        elif option.upper() in ['T', 'TEST']:
            pass
        elif option.upper() in ['R', 'REPORTS']:
            analysis.analysis_menu()
        # ADDING A NEW ENTRY
        elif len(option)>3 and ((time := check_datetime_validity(option[:5], "%H:%M")) or (time := check_datetime_validity(option[:4], "%H%M"))):
            # If working datetime is past the entered time, iterate the day
            if working_datetime.time > time:
                working_datetime += dt.timedelta(days=1)
            working_datetime = working_datetime.replace(hour=time.hour, minute=time.minute)

            with open(config.training_file, 'a') as f:
                f.write("Input=" + str(option) + "\n")
            entry = get_entry_from_user(working_datetime, option=option)  # TODO
            with open(config.training_file, 'a') as f:
                f.write(str(entry) + "\n")

            readwrite.append_entry(entry)
            # Printing log
        else:
            print("Try again!")

def print_recent_entries(df, working_datetime):
    print("DAILY LOG:")
    recent_entries = readwrite.fetch_todays_entries()
    print(readwrite.Entry.header_str)
    for entry in recent_entries:
        print(entry)

def get_entry_from_user(working_datetime, option):

    # user provides option str
    # (parse time handled in console)
    # search for closest match in db
    # prompt 5 closest matches (of full entry: cat/sub/desc)
    # user selects closest match or presses 'n' to write from scratch
    match_list = closest_match([option], df)  # return a few similar entries
    best_entry = match_list[0] # best entry
    while True:
        print(
            f"{BOLD}{MAGENTA}Category: {GREEN}{category}, {MAGENTA}Subcategory: {GREEN}{subcategory}, "
            f"{MAGENTA}Description: {GREEN}{description}{DEFAULT_COLOR}"
        )
        for match, char in zip(match_list[1:], 'qwertyuiop'):
            print(f"{char}) {YELLOW}{match}{DEFAULT_COLOR}")
        print("Use 'c', 's', and 'd' to change category/subcategory/description, or press ENTER to write to log")
        chosen_char = tools.getch()  # get a character from the user
        fields = [{'name': 'category', 'hotkeys': ['C', '1']},
                  {'name': 'subcategory', 'hotkeys': ['S', '2']},
                  {'name': 'description', 'hotkeys': ['D', '3']}]
        if chosen_char == "\n":
            break
        recent_entries = readwrite.fetch_todays_entries(max_entries = 1000)
        for field in fields:
            if chosen_char.upper() in field['hotkeys']:
                # prompt from hotkeys
                tools.prompt_hotkeys(field['name'], )
                # set entry's field
    readwrite.append_to_txt("training_data.txt", "Output=" + str(category) + "-" + str(subcategory) + "-" + str(description) + "\n")


def is_iso_date(string):
    return len(string) >= 10 and all([string[i].isdigit() for i in (0,1,2,3,5,6,8,9)])

def is_military_time(string):
    return len(string) >= 5 and all([string[i].isdigit() for i in (0,1,3,4)])

console("cassia/cassia_diary.txt")