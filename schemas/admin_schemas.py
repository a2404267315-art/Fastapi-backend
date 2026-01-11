from pydantic import BaseModel,Field

class AdminCreateUserRequest(BaseModel):
    user_name:str
    user_password:str

class AdminDeleteUserRequest(BaseModel):
    user_id:int

class AdminBanUserRequest(BaseModel):
    user_id:int

class AdminListAllUserRequest(BaseModel):
    page_size:int=Field(default=10, ge=1, le=100, description="每页条数")
    page_number:int=Field(default=1, ge=1, description="当前页码")

class AdminCreateCharacterRequest(BaseModel):
    character_name:str
    system_prompt:str

class AdminDeleteCharacterRequest(BaseModel):
    character_id:int

class AdminGetChatHistoryRequest(BaseModel):
    chat_id:int
    page_size:int=Field(default=10, ge=1, le=100, description="每页条数")
    page_number:int=Field(default=1, ge=1, description="当前页码")

class AdminGetSoftDeletedUserRequest(BaseModel):
    page_size:int=Field(default=10, ge=1, le=100, description="每页条数")
    page_number:int=Field(default=1, ge=1, description="当前页码")

class AdminNotAllowedWordRequest(BaseModel):
    word:str

class AdminNotAllowedWordRequestByID(BaseModel):
    not_allowed_word_id:int

class AdminGetNotAllowedWordRequest(BaseModel):
    page_size:int=Field(default=10, ge=1, le=100, description="每页条数")
    page_number:int=Field(default=1, ge=1, description="当前页码")
