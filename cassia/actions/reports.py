from cassia.entries import Session, Entry
import questionary

def count_entries():
    with Session() as session:
        return session.query(Entry).count()

def count_categories():
    with Session() as session:
        return session.query(Entry.category).distinct().count()

def count_subcategories():
    with Session() as session:
        return session.query(Entry.subcategory).distinct().count()

def count_date_range():
    with Session() as session:
        return session.query(Entry.date).order_by(Entry.date).first()[0], session.query(Entry.date).order_by(Entry.date.desc()).first()[0]

def reports():
    while True:
        option = questionary.select("Reports:", choices=['Entries', 'Categories', 'Subcategories', 'Date Range', 'Back']).ask()
        if option == 'Entries':
            print(f"Total entries: {count_entries()}")
        elif option == 'Categories':
            print(f"Total categories: {count_categories()}")
        elif option == 'Subcategories':
            print(f"Total subcategories: {count_subcategories()}")
        elif option == 'Date Range':
            start, end = count_date_range()
            print(f"Date range: {start.date()} to {end.date()}")
        elif option == 'Back':
            break
        else:
            print("Try again!")