from sqlalchemy import Column, Integer, String, Text
from project import Base
class Contact(Base):
    __tablename__ = 'contactforms'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text)