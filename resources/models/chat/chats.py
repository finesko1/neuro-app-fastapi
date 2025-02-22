from sqlalchemy import Table, Column, String, Integer, DateTime, MetaData
from sqlalchemy.sql import func
metadata = MetaData()

# Таблица chats базы данных
chats_table = Table(
    'chats',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('created_at', DateTime, default=func.now(), nullable=False),
    Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=False)
)