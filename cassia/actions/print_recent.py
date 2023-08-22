from cassia import entries

def print_recent(num_entries = 10):

    # get all entries and print them
    with entries.Session() as session:
        # get the most recent 10 entries
        recent_entries = session.query(entries.Entry).order_by(entries.Entry.date.desc()).limit(num_entries).all()[::-1]

    print(entries.Entry.header_str)
    total_width = sum(entries.Entry.column_widths) + 3 * len(entries.Entry.column_widths) + 1
    print("─" * total_width)
    for entry in recent_entries:
        print(entry.row_str())
    print("─" * total_width)
