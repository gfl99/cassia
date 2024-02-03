import numpy as np
from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

from cassia.config import db_path
from cassia import embedding

Base = declarative_base()


class Entry(Base):  # inherits from Base
    __tablename__ = 'entries'  # name of the table

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    description = Column(String, nullable=False)
    serialized_embedding = Column(LargeBinary)

    @property
    def embedding(self):
        return np.frombuffer(self.serialized_embedding, dtype=np.float32)

    def get_embedding(self):
        return embedding.embed(str(self))

    def copy(self):
        return Entry(category=self.category, subcategory=self.subcategory, description=self.description)

    def __str__(self):
        s = ''
        for i,attr in enumerate(("category", "subcategory", "description")):
            text = getattr(self, attr) or 'No '+attr
            s += f"{text:<{Entry.column_widths[i]}}"
        return s

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
    input_embedding = embedding.embed(input)
    with Session() as session:
        entries = session.query(Entry).distinct().all()
        entries.sort(key=lambda entry: entry.description)
        distinct_entries = []
        last_description = ""
        for entry in entries:
            if entry.description != last_description:
                distinct_entries.append(entry)
                last_description = entry.description
        distinct_entries.sort(key=lambda entry: entry.embedding @ input_embedding)
        best_entries = distinct_entries[:-6:-1]
        return best_entries


def list_field(field, limit=-1, category=None):
    if not hasattr(Entry, field):
        raise ValueError(f"Entry has no attribute '{field}'")
    filter = (Entry.category == category) if category else True
    with Session() as session:
        entries = session.query(getattr(Entry, field)).filter(filter).distinct().order_by(Entry.date.desc()).limit(limit).all()
        return [getattr(e, field) for e in entries]


def embed_all():
    with Session() as session:
        entries = session.query(Entry).all()
        for entry in tqdm(entries):
            entry.serialized_embedding = entry.get_embedding().tobytes()
        session.commit()
