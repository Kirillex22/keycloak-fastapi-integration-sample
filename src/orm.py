from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    preferred_username = Column(String, unique=True, index=True)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    owner_id = Column(String)