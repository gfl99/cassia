from cassia.entries import Entry, Session

def delete_last_entry():
    with Session() as session:
        last_entry = session.query(Entry).order_by(Entry.date.desc()).first()  # get the most recent entry
        session.delete(last_entry)  # delete the last entry
        session.commit()
        return last_entry
