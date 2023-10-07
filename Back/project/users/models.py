from sqlalchemy import Column, Integer, String, Text,Boolean
from project import Base

#User Table (id ( AUTO INCREMENT) , username as sa tring, hashed password, books ( json object ), isAdmin Bool)
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    date = Column(String(50), nullable=False)
    gender = Column(String(15), nullable=False)
    books = Column(Text)
    isAdmin = Column(Boolean, default=False)