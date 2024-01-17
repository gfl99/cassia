import datetime as dt
import questionary
from cassia import entries


def check_datetime_validity(string, format):
    try:
        return dt.datetime.strptime(string, format)
    except ValueError:
        return False


def parse_option_time(option):
    # does the option begin with HH:MM or HHMM?
    return len(option)>3 and \
            ((check_datetime_validity(option[:5], "%H:%M")) or
             (check_datetime_validity(option[:4], "%H%M")))


def modify_entry(entry):
    # prompt the user to modify the entry
    # return the modified entry
    choices = [questionary.Choice(title='✓ Approve', value='approve', shortcut_key='a'),
               questionary.Choice(title='Edit category', value='category'),
               questionary.Choice(title='Edit subcategory', value='subcategory'),
               questionary.Choice(title='Edit description', value='description')
              ]

    while True:
        action = questionary.rawselect('Approve or edit?', choices=choices).ask()
        if action == 'approve':
            break
        elif action == 'category':
            categories = entries.list_field('category')
            entry.category = questionary.autocomplete('Category:', choices=categories).ask()
        elif action == 'subcategory':
            subcategories = entries.list_field('subcategory')
            entry.subcategory = questionary.autocomplete('Subcategory:', choices=subcategories).ask()
        elif action == 'description':
            entry.description = questionary.text('Description:').ask()
        if action in ('category', 'subcategory', 'description'):
            questionary.print('Updated entry...       ', end='')
            questionary.print(f'{entry}', style='orange bold')
    entry.serialized_embedding = entry.get_embedding().tobytes()


def inject():
    # Prompt user for date
    input_date_str = questionary.text('Enter the date (YYYY-MM-DD):').ask()
    # Validate the date
    date_object = check_datetime_validity(input_date_str, "%Y-%m-%d")
    if not date_object:
        print("Invalid date format. Exiting.")
        return

    # Prompt user for time
    input_time_str = questionary.text('Enter the time (HH:MM):').ask()
    # Validate the time
    time_object = check_datetime_validity(input_time_str, "%H:%M")
    if not time_object:
        print("Invalid time format. Exiting.")
        return

    # Combine date and time into a datetime object
    working_datetime = dt.datetime.combine(date_object.date(), time_object.time())

    # Search for similar entries and prompt user
    match_list = entries.get_templates(input_time_str[5:])
    choices = [questionary.Choice(title=str(entry), value=entry) for entry in match_list]
    chosen_template = questionary.rawselect('Choose a template...', choices=choices).ask()

    # Create a new entry from the chosen template
    new_entry = chosen_template.copy()
    new_entry.date = working_datetime

    # Modify the entry
    modify_entry(new_entry)

    # Add the entry to the database in chronological order
    with entries.Session() as session:
        # Insert the new entry
        session.merge(new_entry)
        # Commit to save changes and maintain chronological order
        session.commit()

# Existing functions remain unchanged
