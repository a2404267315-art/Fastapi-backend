from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from security.verification import get_current_user
from database.management import ConversationManagement, CharacterManagement
from database.utils import get_db
from schemas.user_conversation_schemas import (
    NewConversationCreateRequest,
    MessageRequest,
    GetCharacterRequest,
    GetCurrentUserRequest,
    GetChatHistoryRequest,
    DeleteConversationRequest,
)
from model.model import CyreneLLMModel
from security.limit_request import limiter
from security.not_allowed_words import not_allowed_word

router = APIRouter()


@router.post("/create_chat")
@limiter.limit("10/second")
def new_conversation(
    request: Request,
    body: NewConversationCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character_management = CharacterManagement(db)
    character_name_out = character_management.get_character_by_name(body.character_name)
    if not character_name_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="该角色不存在！"
        )
    conversation_management = ConversationManagement(db)
    chat_name = f"{body.character_name}_{body.chat_name}"
    new_chat = conversation_management.create_conversation(
        current_user.user_id, chat_name
    )
    return {
        "msg": "创建成功！",
        "username": current_user.name,
        "chat_name": chat_name,
        "id": new_chat.id,
        "character_name": body.character_name,
    }


@router.post("/send_message")
@limiter.limit("15/minute")
def send_message_stream(
    request: Request,
    body: MessageRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    found_word = not_allowed_word.check_message(body.message, db)
    if found_word:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"对不起，存在违禁词！打回！",
        )
    conversation_management = ConversationManagement(db)
    character_management = CharacterManagement(db)
    chat = conversation_management.get_conversation(body.chat_id)
    if chat.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此对话"
        )
    if body.whether_regenerate:
        conversation_management.remove_recent_message(body.chat_id)
    conversation_management.send_user_content(
        body.chat_id, history_chat=[{"role": "user", "content": body.message}]
    )
    system_prompt = character_management.get_character_by_name(
        chat.title.split("_")[0]
    ).system_prompt
    history_chat = conversation_management.get_history_chat(body.chat_id)
    try:
        dialog = CyreneLLMModel.create_dialog(
            system_prompt, history_chat=history_chat, model=body.model
        )
        stream_response = dialog.chatting(contents=body.message, model=body.model)
    except Exception as e:
        conversation_management.remove_recent_message(body.chat_id)
        raise HTTPException(
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, detail="内部错误"
        )

    def router_generator():
        try:
            for chunk in stream_response:
                yield chunk
            final_history = dialog.history_chat
            conversation_management.update_history_chat(body.chat_id, final_history)
            print(f"Chat {body.chat_id} history saved.")
        except Exception as e:
            print(f"Stream Error: {e}")
            yield "\n\n[系统错误：生成过程中断，请重试]"
            conversation_management.remove_recent_message(body.chat_id)

    return StreamingResponse(router_generator(), media_type="text/plain")


@router.post("/get_character_name")
@limiter.limit("30/second")
@cache(expire=300)  # 缓存5分钟
async def list_all_character(
    request: Request,
    body: GetCharacterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    current_user = current_user  # 水了个代码
    charater_management = CharacterManagement(db)
    result_table = charater_management.get_character(
        page_size=body.page_size, page_number=body.page_number
    )
    data_list = [row._mapping for row in result_table]
    return data_list


@router.post("/get_current_user_conversation")
@limiter.limit("15/second")
@cache(expire=30)  # 缓存30秒
async def list_current_conversation(
    request: Request,
    body: GetCurrentUserRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.user_id
    conversation_management = ConversationManagement(db)
    result_table = conversation_management.show_user_conversation(
        user_id, page_size=body.page_size, page_number=body.page_number
    )
    data_list = [row._mapping for row in result_table]
    return [data_list]


@router.post("/get_chat_history")
@limiter.limit("100/second")
@cache(expire=10)  # 缓存10秒
async def get_chat_history(
    request: Request,
    body: GetChatHistoryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_management = ConversationManagement(db)
    if not conversation_management.get_conversation(body.chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="对话不存在！"
        )
    if (
        conversation_management.get_conversation(body.chat_id).user_id
        != current_user.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="你偷看别人聊天记录干嘛？"
        )
    return conversation_management.get_certain_history_chat(
        body.chat_id, page_size=body.page_size, page_number=body.page_number
    )


@router.post("/delete_conversation")
@limiter.limit("10/second")
def delete_conversation(
    request: Request,
    body: DeleteConversationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_management = ConversationManagement(db)
    if not conversation_management.get_conversation(body.chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="对话不存在！"
        )
    if (
        conversation_management.get_conversation(body.chat_id).user_id
        != current_user.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="你偷看别人聊天记录干嘛？"
        )
    conversation_management.delete_conversation(body.chat_id)
    return {"msg": "删除成功！"}
