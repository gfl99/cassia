from cassia.tools import colors, MAGENTA, GREEN, BOLD, RED, DEFAULT_COLOR, YELLOW


def delete_last_line_of_txt_file(file, df):
    with open(file, "r+") as f:
        # Read the file line by line
        lines = f.readlines()
        # Clear file contents
        f.seek(0)
        f.truncate()
        # Write back to the file, minus the final line
        f.writelines(lines[:-1])
    # Setting working_datetime to most recent entry
    working_datetime = df.time[len(df) - 1]
    return working_datetime


# Open the file in append mode
def append_to_txt(logfile, appendage):
    with open(logfile, "a") as f:
        # Append the line to the file
        f.write(appendage + "\n")


def write_to_df_and_txt(df, logfile, working_datetime, category, subcategory, description):
    # Write to txt file
    time = working_datetime.strftime("%H:%M")
    append_to_txt(logfile, f"{time}\t{category}\t{subcategory}\t{description}")
    # Write to df
    df.loc[len(df)] = [working_datetime, category, subcategory, description]
    print(
        f"\n{YELLOW}Writing to diary...\n{MAGENTA}{working_datetime}\t{category}\t{subcategory}\t{description}{DEFAULT_COLOR}\n")
    return df
