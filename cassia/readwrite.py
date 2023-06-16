'''
This module contains functions for reading and writing to the diary.
delete_last_entry
✓ append_entry
✗ read_to_dataframe
✓ fetch_todays_entries
'''
from cassia.tools import colors, MAGENTA, GREEN, BOLD, RED, DEFAULT_COLOR, YELLOW

from dataclasses import dataclass
import datetime
from typing import List

from cassia.config import logfile

# we are going to use sqlalchemy to read and write entries to the database
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base  # for creating the base class
from sqlalchemy.orm import sessionmaker  # for creating the session

# create the base class
Base = declarative_base()

@dataclass
class Entry(Base):
    time: datetime.datetime
    category: str
    subcategory: str
    description: str

    @classmethod
    def from_log_line(cls, log_line):
        time, category, subcategory, description = log_line.split("\t")
        time = datetime.datetime.strptime(time, "%Y-%M-%DT%H:%M")
        return cls(time, category, subcategory, description)


    def __str__(self):
        time_str = self.time.strftime("Y-%M-%D %H:%M")
        # use column widths to format the string
        return f"{time_str:<20}{self.category:<15}{self.subcategory:<15}{self.description:<50}"

    headers = ['Time', 'Category', 'Subcategory', 'Description']
    column_widths = [20, 15, 15, 50]
    header_str = "".join([f"{header:<{width}}" for header, width in zip(headers, column_widths)])


# Open the file in append mode
def append_to_txt(logfile, appendage):
    with open(logfile, "a") as f:
        # Append the line to the file
        f.write(appendage + "\n")

def delete_last_entry():
    with open(logfile, "r+") as f:
        # Read the file line by line
        lines = f.readlines()
        # Clear file contents
        f.seek(0)
        f.truncate()
        # Write back to the file, minus the final line
        f.writelines(lines[:-1])
        # TODO: could be O(1) instead of O(n) if we seek end of file

def append_entry( entry: Entry):
    # Write to txt file
    time = entry.time.strftime("%H:%M")
    with open(logfile, "a") as f:
        f.write(f"{time}\t{entry.category}\t{entry.subcategory}\t{entry.description}" + "\n")

def fetch_todays_entries(max_entries = 20) -> List[Entry]:
    today = datetime.date.today()
    lines = logfile.read_text().splitlines()
    recent_lines = lines[-max_entries:]
    recent_entries = [Entry.from_log_line(line) for line in recent_lines]
    return recent_entries


