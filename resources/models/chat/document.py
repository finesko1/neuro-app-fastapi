from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from database.connect import Base
from resources.models.chat.chats import Chats

class UploadFilesModel(Base):
    __tablename__ = 'uploaded_files'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    chat_id:Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete="CASCADE"), nullable = False)
    path: Mapped[str] = mapped_column(nullable = False)
    original_name: Mapped[str] = mapped_column(nullable = False)
    created_at: Mapped[datetime] = mapped_column(nullable = False, default = func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable = False, default = func.now(), onupdate = func.now())