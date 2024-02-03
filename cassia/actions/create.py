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
    approve_choice = questionary.Choice(title='✓ Approve', value='approve', shortcut_key='a')
    edit_choices = [questionary.Choice(title='Edit category', value='category', shortcut_key='c'),
                    questionary.Choice(title='Edit subcategory', value='subcategory', shortcut_key='s'),
                    questionary.Choice(title='Edit description', value='description', shortcut_key='d')
                   ]

    while True:
        approve_choice.disabled = not all((entry.category, entry.subcategory, entry.description))
        edit_choices.sort(key=lambda choice: getattr(entry, choice.value) is not None)  # put attributes that are None at the beginning
        choices = [approve_choice] + edit_choices
        action = questionary.rawselect('Approve or edit?', choices=choices).ask()
        if action == 'approve':
            break
        elif action == 'category':
            categories = entries.list_field('category')
            entry.category = questionary.autocomplete('Category:', choices=categories).ask() if categories else questionary.text('Category:').ask()
        elif action == 'subcategory':
            subcategories = entries.list_field('subcategory')
            entry.subcategory = questionary.autocomplete('Subcategory:', choices=subcategories).ask() if subcategories else questionary.text('Subcategory:').ask()
        elif action == 'description':
            entry.description = questionary.text('Description:').ask()
        if action in ('category', 'subcategory', 'description'):
            questionary.print('Updated entry...       ', end='')
            questionary.print(f'{entry}', style='orange bold')
    entry.serialized_embedding = entry.get_embedding().tobytes()

def create(input):

    # parse input time
    time = parse_option_time(input)
    # get the most recent date and update it with the input time
    with entries.Session() as session:
        most_recent_entry = session.query(entries.Entry).order_by(entries.Entry.date.desc()).first()
        working_datetime = most_recent_entry.date if most_recent_entry else dt.datetime.now()
    if working_datetime.time() > time.time():
        working_datetime += dt.timedelta(days=1)
    working_datetime = working_datetime.replace(hour=time.hour, minute=time.minute)
    # search similar entries
    match_list = entries.get_templates(input[5:])
    if match_list:
        best_entry = match_list[0]
        # prompt the closest matches
        choices = [questionary.Choice(title=str(entry), value=entry) for entry in match_list]
        chosen_template = questionary.rawselect('Choose a template...', choices=choices).ask()
        # create a new entry from the chosen template
        new_entry = chosen_template.copy()
    else:
        new_entry = entries.Entry()
    new_entry.date = working_datetime  # set the date to the working datetime
    # modify the entry
    modify_entry(new_entry)
    # add the entry to the database
    with entries.Session() as session:
        session.merge(new_entry)
        session.commit()
