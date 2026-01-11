from typing import Dict,List,Any
from datetime import datetime
from sqlalchemy import String,BigInteger,JSON,Boolean,ForeignKey,func,text,Text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column, relationship
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="users"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    user_id:Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True,index=True)
    name:Mapped[str]=mapped_column(String(50),unique=True)
    password:Mapped[str]=mapped_column(String(1024))
    is_banned:Mapped[bool]=mapped_column(Boolean,server_default=text("false"))
    is_admin:Mapped[bool]=mapped_column(Boolean,server_default=text("false"))
    is_deleted:Mapped[bool]=mapped_column(Boolean,server_default=text("false"))
    conversations:Mapped[List["Conversation"]]=relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

class Conversation(Base):
    __tablename__="conversations"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True,index=True)
    user_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("users.user_id"))
    owner:Mapped["User"] = relationship(
        back_populates="conversations" # 指向对方模型里的属性名
    )
    chat:Mapped[List["Chat"]]=relationship(back_populates="owner",cascade="all,delete-orphan")
    title:Mapped[str]=mapped_column(String(50),default="新对话")
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

class Chat(Base):
    __tablename__="chats"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True)
    chat_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("conversations.id"),index=True)
    owner:Mapped["Conversation"]=relationship(back_populates="chat")
    role:Mapped[str]=mapped_column(String(50))
    content:Mapped[str]=mapped_column(Text)
    create_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),server_default=func.now()
    )

class Character(Base):
    __tablename__="character"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True,index=True)
    name:Mapped[str]=mapped_column(String(50),unique=True)
    system_prompt:Mapped[str]=mapped_column(Text)

class NotAllowedWord(Base):
    __tablename__="not_allowed_words"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True,index=True)
    word:Mapped[str]=mapped_column(String(50),unique=True)