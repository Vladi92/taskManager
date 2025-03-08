from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"  # Table name in PostgreSQL
    id = Column(Integer, primary_key=True, autoincrement=True)  # SERIAL
    title = Column(String(255), nullable=False)  # VARCHAR(255) NOT NULL
    description = Column(Text)  # TEXT
    status = Column(String(50), default="pending")  # VARCHAR(50) DEFAULT 'pending'
    created_at = Column(TIMESTAMP, server_default=func.now())  # TIMESTAMP DEFAULT now()