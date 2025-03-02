from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from database.connect import Base
from resources.models.chat.chats import Chats

class Messages(Base):
    """
    Модель для работы с таблицей чатов - *Messages*
    """
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    global_collection: Mapped[str] = mapped_column(nullable=True)
    local_collection: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Messages(id={self.id}, chat_id={self.chat_id}, role={self.role}, content={self.content},global_collection={self.global_collection},local_collection={self.local_collection} created_at={self.created_at}, updated_at={self.updated_at})>"