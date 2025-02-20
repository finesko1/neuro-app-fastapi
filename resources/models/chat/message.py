from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)

    # Связь с моделью чата
    chat = relationship("Chat", back_populates="messages")