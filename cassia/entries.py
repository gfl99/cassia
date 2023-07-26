from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

from cassia.config import db_path

Base = declarative_base()


class Entry(Base):  # inherits from Base
    __tablename__ = 'entries'  # name of the table

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    description = Column(String, nullable=False)
    embedding = Column(LargeBinary)

    def copy(self):
        return Entry(category=self.category, subcategory=self.subcategory, description=self.description)

    def __str__(self):
        return (f"{self.category:<{Entry.column_widths[1]}}   "
                f"{self.subcategory:<{Entry.column_widths[2]}}   "
                f"{self.description:<{Entry.column_widths[3]}}")

    def row_str(self):
        time_str = self.date.strftime("%Y-%m-%d    %H:%M")
        # use column widths to format the string
        time_width, cat_width, subcat_width, desc_width = Entry.column_widths
        return f"│  {time_str:<{time_width}}│  {self.category:<{cat_width}}│  {self.subcategory:<{subcat_width}}│  {self.description:<{desc_width}}│"

    headers = ['Time', 'Category', 'Subcategory', 'Description']
    column_widths = [25, 20, 20, 120]
    header_str = "   " + "   ".join([f"{header:<{width}}" for header, width in zip(headers, column_widths)])



engine = create_engine(f'sqlite:///{db_path}')

# to ensure that the database schema matches the model
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)  # factory for creating sessions

def get_templates(input: str):
    # return the five most recent entries,
    with Session() as session:
        return session.query(Entry).order_by(Entry.date.desc()).limit(5).all()

def list_field(field, limit=-1, category=None):
    if not hasattr(Entry, field):
        raise ValueError(f"Entry has no attribute '{field}'")
    filter = Entry.category == category if category else True
    with Session() as session:
        return [getattr(e, field) for e in session.query(getattr(Entry, field)).filter(filter).distinct().order_by(Entry.date.desc()).limit(limit).all()]
