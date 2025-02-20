from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Связь с моделью сообщений
    messages = relationship("Message", back_populates="chat")