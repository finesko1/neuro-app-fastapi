from sqlalchemy import Table, Column, String, Integer, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime
from database.connect import Base
from datetime import datetime
#metadata = MetaData()
## Таблица chats базы данных
#chats_table = Table(
#    'chats',
#    metadata,
#    Column('id', Integer, primary_key=True),
#    Column('created_at', DateTime, default=func.now(), nullable=False),
#    Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=False)
#)

class Chats(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    update_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now(), nullable=False)
    #chat_id: Mapped[int] = mapped_column(unique=True)
# Вставить данные db.add(Chats()) + db.commit
