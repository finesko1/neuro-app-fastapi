from sqlalchemy import Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime, BigInteger
from datetime import datetime
from database.connect import Base
from resources.models.chat.chats import Chats
#metadata = MetaData()
#messages = Table(
#    'messages',
#    metadata,
#    Column('id', Integer, primary_key=True),
#    Column('chat_id', Integer, ForeignKey('chats.id')),
#    Column('role', String),
#    Column('created_at', DateTime, default=func.now(), nullable=False),
#    Column('created_at', DateTime, default=func.now(), onupdate=func.now(), nullable=False),
#)

class Messages(Base):
    """
    Модель для работы с таблицей чатов - *Messages*
    """
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Messages(id={self.id}, chat_id={self.chat_id}, role={self.role}, content={self.content} created_at={self.created_at}, updated_at={self.updated_at})>"