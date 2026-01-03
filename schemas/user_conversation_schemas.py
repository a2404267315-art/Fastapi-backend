from pydantic import BaseModel,Field

class NewConversationCreateRequest(BaseModel):
    chat_name:str
    character_name:str

class MessageRequest(BaseModel):
    message:str
    chat_id:int
    model:str
    whether_regenerate:bool

class GetCharacterRequest(BaseModel):
    page_size:int=Field(default=10, ge=1, le=100, description="每页条数")
    page_number:int=Field(default=1, ge=1, description="当前页码")

class GetCurrentUserRequest(BaseModel):
    page_size:int=Field(default=10, ge=1, le=100, description="每页条数")
    page_number:int=Field(default=1, ge=1, description="当前页码")

class GetChatHistoryRequest(BaseModel):
    chat_id:int

