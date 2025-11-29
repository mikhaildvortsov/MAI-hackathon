"""Database models for company context storage."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class CompanyContext(Base):
    """Model for storing company context information."""
    
    __tablename__ = "company_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Название контекста")
    context_text = Column(Text, nullable=False, comment="Текст корпоративного контекста")
    description = Column(Text, nullable=True, comment="Описание контекста")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EmailThread(Base):
    """Model for storing email conversation threads."""
    
    __tablename__ = "email_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(500), nullable=False, index=True, comment="Тема переписки")
    company_context_id = Column(Integer, ForeignKey("company_contexts.id"), nullable=True, comment="ID корпоративного контекста")
    extra_directives = Column(Text, nullable=True, comment="Дополнительные указания для всей переписки (JSON массив)")
    custom_prompt = Column(Text, nullable=True, comment="Дополнительное описание задачи для всей переписки")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    messages = relationship("EmailMessage", back_populates="thread", cascade="all, delete-orphan")


class EmailMessage(Base):
    """Model for storing individual emails in a conversation thread."""
    
    __tablename__ = "email_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("email_threads.id"), nullable=False, index=True, comment="ID переписки")
    message_type = Column(String(20), nullable=False, comment="Тип сообщения: 'incoming' или 'outgoing'")
    subject = Column(String(500), nullable=False, comment="Тема письма")
    body = Column(Text, nullable=False, comment="Текст письма")
    sender_name = Column(String(255), nullable=True, comment="Имя отправителя")
    sender_position = Column(String(255), nullable=True, comment="Должность отправителя")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    generation_time_seconds = Column(Float, nullable=True, comment="Время генерации письма в секундах (только для outgoing)")
    
    thread = relationship("EmailThread", back_populates="messages")

