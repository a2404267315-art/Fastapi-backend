from typing import Any

from sqlalchemy.orm import Session,load_only
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from .database_structure import User,Conversation,Character

class UserManagement:
    def __init__(self,db:Session):
        self.db=db
    
    def get_user_by_name(self,name:str):
        return self.db.execute(
            select(User).where(User.name==name)
            ).scalar_one_or_none()        #要使用user_id就在函数后边标个user_id:get_user_by_name(name).user_id
    
    def get_user_by_id(self,user_id:int):
        return self.db.execute(
            select(User).where(User.user_id==user_id)
            ).scalar_one_or_none()
    
    def show_user(self,page_size,page_number):
        return self.db.execute(
            select(User.user_id,User.name,User.is_admin,User.is_banned).where(User.is_deleted==False).limit(page_size).offset((page_number-1)*page_size)
        )
    
    def create_user(self,name:str,password:str,is_admin:bool=False,is_banned:bool=False,is_deleted:bool=False):
        existing_user=self.get_user_by_name(name)
        if existing_user:
            return existing_user
        db_user=User(name=name,
                     password=password,
                     is_admin=is_admin,
                     is_deleted=is_deleted,
                     is_banned=is_banned,
                     )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def change_user_password(self,user_id:int,new_password):
        user=self.get_user_by_id(user_id)
        if not user or user.is_deleted:
            return False
        user.password=new_password
        self.db.commit() 
        return True

    def soft_user_delete(self,user_id:int):
        user=self.get_user_by_id(user_id)
        if not user or user.is_admin:
            return False
        user.is_deleted=True
        self.db.commit()
        return True
    
    def undo_soft_user_delete(self,user_id:int):
        user=self.get_user_by_id(user_id)
        if not user or not user.is_deleted:
            return False
        user.is_deleted=False
        self.db.commit()
        self.db.refresh(user)
        return True
    
    def true_user_delete(self,user_id:int):
        user=self.get_user_by_id(user_id)
        if not user or not user.is_deleted or user.is_admin:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
    
    def ban_user(self,user_id):
        user=self.get_user_by_id(user_id)
        if not user or user.is_deleted or user.is_banned or user.is_admin:
            return False
        user.is_banned=True
        self.db.commit()
        self.db.refresh(user)
        return True

    def unban_user(self,user_id):
        user=self.get_user_by_id(user_id)
        if not user or user.is_deleted or not user.is_banned:
            return False
        user.is_banned=False
        self.db.commit()
        self.db.refresh(user)
        return True
    
    def get_soft_deleted_users(self,page_size,page_number):
        return self.db.execute(
            select(User.name,User.user_id).where(User.is_deleted==True).limit(page_size).offset((page_number-1)*page_size)
            )
    
class ConversationManagement:
    def __init__(self,db:Session):
        self.db=db
    
    def create_conversation(self,user_id:int,title:str="新对话",):
        new_chat=Conversation(
            user_id=user_id,
            title=title,
            history_chat=[]
        )
        self.db.add(new_chat)
        self.db.commit()
        self.db.refresh(new_chat)
        return new_chat
    
    def get_conversation(self,chat_id:int):
        return self.db.execute(
            select(Conversation).where(Conversation.id==chat_id)
            ).scalar_one_or_none()

    def show_all_conversation(self,page_size,page_number):
        return self.db.execute(
            select(Conversation.id,Conversation.user_id,User.name,Conversation.title).join(User).where(User.is_deleted==0).limit(page_size).offset((page_number-1)*page_size)
            )
    
    def show_user_conversation(self,user_id,page_size,page_number):
        return self.db.execute(
            select(Conversation.id,Conversation.title).where(Conversation.user_id==user_id).limit(page_size).offset((page_number-1)*page_size)
            )
    
    def update_history_chat(self,chat_id:int,history_chat:list[dict[str,Any]]):
        chat=self.get_conversation(chat_id)
        if not chat:
            return False
        chat.history_chat=history_chat
        flag_modified(chat, "history_chat")
        self.db.commit()
        self.db.refresh(chat)
        return True
    
    def get_history_chat(self,chat_id:int):
        chat=self.get_conversation(chat_id)
        if not chat:
            return False
        if chat.history_chat is None:
            return []
        if len(chat.history_chat)>20:
            length=len(chat.history_chat)
            history_chat=chat.history_chat[length-20:length]
        else:
            history_chat=chat.history_chat
        return history_chat
    
    def get_certain_history_chat(self,chat_id:int):
        chat=self.get_conversation(chat_id)
        if not chat:
            return False
        if chat.history_chat is None:
            return []
        return chat.history_chat
    
    def delete_conversation(self,chat_id:int):
        chat=self.get_conversation(chat_id)
        if not chat:
            return False
        self.db.delete(chat)
        self.db.commit()
        return True
    
    def remove_recent_message(self,chat_id:int):
        history_chat=self.get_history_chat(chat_id)
        if len(history_chat) < 2:
            self.update_history_chat(chat_id, [])
            return True
        history_chat=history_chat[:-2]
        self.update_history_chat(chat_id,history_chat)
        return True


class CharacterManagement:
    def __init__(self,db:Session):
        self.db=db

    def create_character(self,name,system_prompt):
        new_character=Character(
            name=name,
            system_prompt=system_prompt
        )
        self.db.add(new_character)
        self.db.commit()
        self.db.refresh(new_character)
        return new_character
    
    def get_character_by_name(self,name):
        return self.db.execute(
            select(Character).where(Character.name==name)
            ).scalar_one_or_none()
    
    def get_character_by_id(self,id):
        return self.db.execute(
            select(Character).where(Character.id==id)
            ).scalar_one_or_none()
    
    def update_character(self,name,system_prompt):
        character=self.get_character_by_name(name)
        if not character:
            return False
        character.system_prompt=system_prompt
        self.db.commit()
        self.db.refresh(character)
        return True
    
    def delete_character(self,id):
        character=self.get_character_by_id(id)
        if not character:
            return False
        self.db.delete(character)
        self.db.commit()
        return True
    
    def get_character(self,page_size,page_number):
        return self.db.execute(select(Character.id,Character.name).limit(page_size).offset((page_number-1)*page_size))

    



    
    
