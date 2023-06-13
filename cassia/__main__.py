import datetime as dt
import time
import pandas as pd
from fuzzywuzzy import fuzz
from cassia import readwrite, analysis, config, tools
from cassia.tools import colors, YELLOW, GREEN, RED, DEFAULT_COLOR, BOLD, MAGENTA


def print_days_entries(df, working_datetime):
    print("DAILY LOG:")
    print(df[df['time'].dt.date == (working_datetime.date())])


def console(logfile):
    # Greet User
    print("Hello!")
    # Import data
    working_datetime, df = import_data(logfile)
    print_days_entries(df, working_datetime)
    while True:
        # Print all entries from current day
        print("----------------------------------------")
        # Prompt input
        option = input(
            f"\n{YELLOW}Options: New Entry [%H:%M], [R]eports, Today's [E]ntries, [D]elete last line, [L]ist cat/sub/desc, View [F]iltered data, e[X]it: {DEFAULT_COLOR}")
        # Input parsing for exit
        if option.upper() in ['L', 'LIST']:
            field = tools.prompt_hotkeys("field", ['category', 'subcategory', 'description'], allow_new=False)
            print(analysis.list_unique_values(df, field))
        elif option.upper() in ['X', 'EXIT', 'QUIT']:
            break
        # ...for deleting the last row
        elif option.upper() in ['D', 'DELETE']:
            # Delete from df
            df = df.drop(df.index[-1])
            # Delete from txt file
            working_datetime = readwrite.delete_last_line_of_txt_file(logfile, df)
        # ...for adding a new entry
        elif len(option) > 3 and (check_datetime_validity(option, "%H:%M") or check_datetime_validity(option, "%H%M")):
            # Set hour and minute based on format
            if check_datetime_validity(option, "%H:%M"):
                hour = dt.datetime.strptime(option, "%H:%M").hour
                minute = dt.datetime.strptime(option, "%H:%M").minute
            elif check_datetime_validity(option, "%H%M"):
                hour = dt.datetime.strptime(option, "%H%M").hour
                minute = dt.datetime.strptime(option, "%H%M").minute
            # If working datetime is past the entered time, iterate the day
            entered_datetime = working_datetime.replace(hour=hour, minute=minute)
            if working_datetime > entered_datetime:
                working_datetime = entered_datetime + dt.timedelta(days=1)
                readwrite.append_to_txt(logfile, working_datetime.isoformat()[0:10])
            else:
                working_datetime = entered_datetime
            # Write to df
            df = add_entry(logfile, working_datetime, df)
            # Printing log
            print_days_entries(df, working_datetime)
        elif option.upper() in ['T', 'TEST']:
            test()
        elif option.upper() in ['F', 'FILTER']:
            print_filtered(df)
        elif option.upper() in ['E', 'ENTRIES']:
            print_days_entries(df, working_datetime)
        elif option.upper() in ['R', 'REPORTS']:
            analysis.analysis_menu(df)
        else:
            print("Try again!")


def add_entry(logfile, working_datetime, df):
    option = input("Enter a keyword or use 'n' to write from scratch:\n")
    # Input parsing for entries from scratch
    if option.upper() in ['N', 'NEW']:
        category, subcategory, description = write_from_scratch(df)
    # Input parsing for keyword entries
    else:
        readwrite.append_to_txt("training_data.txt", "Input=" + str(option) + "\n")
        match_list = (closest_match([option], df))
        triplet = tools.prompt_hotkeys('previous entry', match_list, full_entry=True)
        if triplet is None:
            category, subcategory, description = write_from_scratch(df)
        else:
            category, subcategory, description = triplet.split("\t")
            while True:
                print(
                    f"{BOLD}{MAGENTA}Category: {GREEN}{category}, {MAGENTA}Subcategory: {GREEN}{subcategory}, {MAGENTA}Description: {GREEN}{description}{DEFAULT_COLOR}")
                option = input("Use 'c', 's', and 'd' to change category/subcategory/description, "
                               "or press ENTER to write to log")
                if str(option).upper() in ['C', 'CATEGORY', '1']:
                    category = input("Change category name to: ")
                elif str(option).upper() in ['S', 'SUBCATEGORY', '2']:
                    subcategory = input("Change subcategory name to: ")
                elif str(option).upper() in ['D', 'DESCRIPTION', '3']:
                    description = input("Change description name to: ")
                elif option == "":
                    break
                else:
                    print("Try again!")
    df = readwrite.write_to_df_and_txt(df, logfile, working_datetime, category, subcategory, description)
    readwrite.append_to_txt("training_data.txt", "Output=" + str(category) + "-" + str(subcategory) + "-" + str(description) + "\n")
    return df


def write_from_scratch(df):
    # Set default blank description
    # Prompt with category list
    category_list = sorted(df['category'].unique())
    category = tools.prompt_hotkeys('category', category_list)
    filtered_df = df.loc[df['category'] == category, :]
    # Prompt with subcategory list
    subcategory_list = sorted(filtered_df['subcategory'].unique())
    subcategory = tools.prompt_hotkeys('subcategory', subcategory_list)
    filtered_df = filtered_df.loc[filtered_df['subcategory'] == subcategory, :]
    # Prompt with description list
    description_list = sorted(filtered_df['description'].unique())
    if '' in description_list:  # Removing blanks if they exist, otherwise '' will appear as a hotkey
        description_list.remove('')
    print(description_list)
    description = tools.prompt_hotkeys('description', description_list, allow_blanks=True, character_limit=60)
    return category, subcategory, description


def closest_match(keyword_list, df, match_limit=5):
    # Initialize match list
    matches = dict()

    # Iterate over each column in the dataframe
    for row in df.iterrows():
        # Defaults
        data = [row[1]['category'], row[1]['subcategory'], row[1]['description']]
        data_str = f"{data[0]}\t{data[1]}\t{data[2]}"
        match_values = [0, 0, 0]

        for keyword in keyword_list:
            for index, value in enumerate(data):
                if keyword.upper() in value.upper():
                    match_values[index] = 100  # If keyword is contained exactly in value, set similarity to 100
                match_values[index] = max(fuzz.token_set_ratio(keyword, value), match_values[index])
        similarity_score = match_values[0] ** 2 + match_values[1] ** 2 + match_values[2] ** 2
        # Initial dictionary fill
        if len(matches) < match_limit and data_str not in matches:
            matches[data_str] = similarity_score
        # Check if entry is better than any current ones
        elif any(similarity_score > value for value in matches.values()) and data_str not in matches:
            matches[data_str] = similarity_score
            # Drop the lowest value in the dictionary
            del matches[min(matches.keys(), key=lambda k: matches[k])]
    sorted_dict = [key for key, value in sorted(matches.items(), key=lambda x: x[1], reverse=True)]
    return sorted_dict


def check_datetime_validity(string, date_format):
    try:
        dt.datetime.strptime(string, date_format)
        return True
    except ValueError:
        return False

def is_iso_date(string):
    return len(string) >= 10 and all([string[i].isdigit() for i in (0,1,2,3,5,6,8,9)])

def is_military_time(string):
    return len(string) >= 5 and all([string[i].isdigit() for i in (0,1,3,4)])

def import_data(logfile):
    start_time = time.time()
    # Initializing data frame
    data = pd.DataFrame({'time': [], 'category': [], 'subcategory': [], 'description': []})
    # Open timelog, ignore first two lines (containing: set vim modelines & headers
    new_data = open(logfile, "r").read().split("\n")[2:]
    # Parsing each line
    columns = None
    for line, i in enumerate(new_data):
        # If the line is a date, change the date
        #if check_datetime_validity(line, "%Y-%m-%d"):
        if is_iso_date(line):
            working_datetime = dt.datetime.strptime(line,
                                                    "%Y-%m-%d")  # If the line starts with a time, save to dataframe
            midnight = dt.datetime.combine(working_datetime.date(), dt.time.min)
            if columns is not None and len(columns) == 4:
                data.loc[len(data)] = [midnight, columns[1], columns[2], columns[3]]
            elif columns is not None and len(columns) == 3:
                data.loc[len(data)] = [midnight, columns[1], columns[2], ""]
            # Adding midnight entry
        #elif check_datetime_validity(line[0:5], "%H:%M"):
        elif is_military_time(line[0:5]):
            columns = line.split('\t')
            hour, minute = int(line[0:2]), int(line[3:5])
            working_datetime = working_datetime.replace(hour=hour, minute=minute)
            if len(columns) == 4:
                data.loc[len(data)] = [working_datetime, columns[1], columns[2], columns[3]]
            elif len(columns) == 3:
                data.loc[len(data)] = [working_datetime, columns[1], columns[2], ""]
            else:
                print(f"While importing data, the following line could not be parsed:\n{line}")

        elif line == "":
            pass
        else:
            raise ValueError(f"While importing data, the following line could not be parsed:\n{line} @ line #{i+1}")

    # Return data w/durations
    end_time = time.time()
    print(end_time - start_time)
    return working_datetime, data


def print_filtered(df):
    df = tools.add_durations(df)
    fields = ['category', 'subcategory', 'description', 'Start Time', 'End Time']
    for field in fields:
        if field not in ['Start Time', 'End Time']:
            print(analysis.list_unique_values(df, field))
        selection = input(f"Please enter a {field} (press ENTER to skip):")
        if selection.upper() in ['X', 'EXIT']:
            break
        if field == 'Start Time':
            date = 'After'
            field = 'time'
        elif field == 'End Time':
            date = 'Before'
            field = 'time'
        else:
            date = None
        # If field was skipped, don't filter
        if selection != "":
            df = analysis.filter_df(df, field, selection, date=date)
    # Printing filtered df
    print("Filtered results:\n")
    print(df)


def test():
    working_datetime, df = import_data('cassia/cassia_diary.txt')

console("cassia/cassia_diary.txt")
