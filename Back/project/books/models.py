from sqlalchemy import Column, Integer, String, Text
from project import Base
#Book Table (id (AUTO INCREMENT), name as a string, Author, image path, amount of copies defaults to 0 )
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    author = Column(String(100))
    release = Column(String(4))
    image = Column(String(100))
    copies = Column(Integer, default=0)