import sys, tty, termios

# Styling list
MAGENTA, GREEN, BOLD, RED, DEFAULT_COLOR, YELLOW = "\033[95m", "\033[32m", "\33[0;1m", "\033[31m", "\033[0m", "\033[93m"
colors = [MAGENTA, GREEN, BOLD, RED, DEFAULT_COLOR, YELLOW]


# Calculating durations
def add_durations(data):
    data['duration'] = ""
    for i in range(len(data) - 1):
        data.loc[i, 'duration'] = int((data.time[i + 1] - data.time[i]) / pd.Timedelta(minutes=1))
    # Convert type from int64 to int
    #    data.Duration = data.duration.to_dict()
    # Return data
    return data[1:-1]

# read a character from the user without
# them having to press enter
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        #tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def prompt_hotkeys(name, option_list, allow_new=True,
                   max_hotkeys=55, allow_blanks=False, character_limit=15, full_entry=False):
    while True:
        # Prompt the user to select an option
        print(f"Select a {name}:\n")

        # If full_entry=True, print headers for fields
        if full_entry:
            print("   CATEGORY    SUBCATEGORY         DESCRIPTION")

        # Display the sorted list items, up to the specified maximum number of hotkeys
        for i, (key) in enumerate(option_list[:max_hotkeys - 1]):
            print(f"{colors[i % 2]}{i + 1}) {key}".expandtabs(20))

        # Add new option
        if allow_new:
            print(f"{RED} N) Add new {name}\n")

        # Read the user's input
        if allow_blanks:
            choice = input(f"{YELLOW}Enter your selection (or press ENTER to skip field): ")
        else:
            choice = input(f"{YELLOW}Enter your selection: ")

        # Reset formatting
        print(colors[4])

        try:
            # Convert the user's input to an integer and use it to index into the option_list
            index = int(choice) - 1
            if index >= len(option_list):
                # The user entered an invalid hotkey
                print("Invalid hotkey. Please try again.")
                continue

            # Get the selected key and value
            choice = option_list[index]
            return choice
        except ValueError:
            # The user's input is not a valid integer
            # Check if the user wants to add a new value
            if choice.upper() == "N":
                if full_entry:
                    return None
                # Prompt the user to enter a new value
                while True:
                    new_value = input(f"Enter a new {name}: ")
                    if len(new_value) < character_limit:
                        break
                    else:
                        print(f"Too long, character limit = {character_limit}")

                return new_value
            # Check if the user left the field blank (only work if allow_blanks==True)
            elif choice == "" and allow_blanks:
                return choice
            elif choice.upper() == "X":
                exit()
