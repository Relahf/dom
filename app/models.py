from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    apartment = Column(String(20), index=True)
    role = Column(String(20), default='resident')
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    llm_daily_limit = Column(Integer, nullable=True)
    llm_requests_today = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship('ChatMessage', back_populates='sender', foreign_keys='ChatMessage.sender_id')
    files = relationship('File', back_populates='owner')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False)
    sender = relationship('User', back_populates='messages', foreign_keys=[sender_id])

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    filename = Column(String(255))
    file_path = Column(String(255))
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='files')

class WikiPage(Base):
    __tablename__ = 'wiki_pages'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True, index=True)
    slug = Column(String(255), unique=True)
    content = Column(Text)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Mail(Base):
    __tablename__ = 'mail'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    recipient_id = Column(Integer, ForeignKey('users.id'))
    subject = Column(String(255))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Complaint(Base):
    __tablename__ = 'complaints'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    content = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    status = Column(String(20), default='new')
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Announcement(Base):
    __tablename__ = 'announcements'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(255))
    content = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class PollOption(Base):
    __tablename__ = 'poll_options'
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'))
    text = Column(String(255))

class PollVote(Base):
    __tablename__ = 'poll_votes'
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'))
    option_id = Column(Integer, ForeignKey('poll_options.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
