from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class Entry(Base):  # inherits from Base
    __tablename__ = 'entries'  # name of the table

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    description = Column(String, nullable=False)
    embedding = Column(LargeBinary)

    def __str__(self):
        time_str = self.date.strftime("Y-%M-%D %H:%M")
        # use column widths to format the string
        return f"{time_str:<20}{self.category:<15}{self.subcategory:<15}{self.description:<50}"

    headers = ['Time', 'Category', 'Subcategory', 'Description']
    column_widths = [20, 15, 15, 50]
    header_str = "".join([f"{header:<{width}}" for header, width in zip(headers, column_widths)])


engine = create_engine('sqlite:///cassia.db')

# to ensure that the database schema matches the model
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)  # factory for creating sessions