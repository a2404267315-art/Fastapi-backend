from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

from schemas.admin_schemas import (
    AdminCreateUserRequest,
    AdminDeleteUserRequest,
    AdminBanUserRequest,
    AdminGetSoftDeletedUserRequest,
    AdminListAllUserRequest,
    AdminCreateCharacterRequest,
    AdminDeleteCharacterRequest,
    AdminNotAllowedWordRequest,
    AdminGetChatHistoryRequest,
    AdminNotAllowedWordRequestByID,
    AdminGetNotAllowedWordRequest,
)
from schemas.admin_schemas import AdminDeleteConversationRequest
from security.verification import get_current_admin
from security.security import SecurityUtils
from database.utils import get_db
from database.management import (
    UserManagement,
    ConversationManagement,
    CharacterManagement,
    NotallowedWordManagement,
)
from security.limit_request import limiter

router = APIRouter()


@router.post("/create_user")
@limiter.limit("10/second")
def create_user(
    request: Request,
    body: AdminCreateUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_mananger = UserManagement(db)
    password = SecurityUtils.get_password_hash(body.user_password)
    try:
        success = user_mananger.create_user(name=body.user_name, password=password)
        if success:
            user = user_mananger.get_user_by_name(body.user_name)
            return {
                "status": "ok",
                "msg": "注册成功",
                "user_id": user.user_id,
                "user_name": body.user_name,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="对不起，用户已经存在！"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/soft_delete")
@limiter.limit("10/second")
def soft_delete_user(
    request: Request,
    body: AdminDeleteUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    if not user_management.soft_user_delete(body.user_id):
        user = user_management.get_user_by_id(body.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该用户不存在"
            )
        if user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该用户是管理员"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该用户已被删除或软删除"
        )
    else:
        return {"msg": "软删除操作成功", "user_id": body.user_id}


@router.post("/undo_soft_delete")
@limiter.limit("10/second")
def undo_soft_delete_user(
    request: Request,
    body: AdminDeleteUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    if not user_management.undo_soft_user_delete(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该用户没有删除"
        )
    else:
        return {"msg": "该用户取消软删除成功！", "user_id": body.user_id}


@router.delete("/true_delete", description="谨慎操作！！！！")
@limiter.limit("10/second")
def true_delete_user(
    request: Request,
    body: AdminDeleteUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    if not user_management.true_user_delete(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该用户不存在或未被软删除"
        )
    else:
        return {"msg": "该用户已被删除", "user_id": body.user_id}


@router.post("/ban")
@limiter.limit("100/second")
def ban_user(
    request: Request,
    body: AdminBanUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    if not user_management.ban_user(body.user_id):
        user = user_management.get_user_by_id(body.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该用户不存在"
            )
        if user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该用户是管理员"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已被删除或已经被封禁了",
        )
    else:
        return {"msg": "该用户已封禁", "user_id": body.user_id}


@router.post("/unban")
@limiter.limit("100/second")
def unban_user(
    request: Request,
    body: AdminBanUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    if not user_management.unban_user(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已被删除或已经被封禁了",
        )
    else:
        return {"msg": "该用户已解封", "user_id": body.user_id}


@router.post("/all_user")
@limiter.limit("100/second")
def list_all_user(
    request: Request,
    body: AdminListAllUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    result_table = user_management.show_user(
        page_size=body.page_size, page_number=body.page_number
    )
    data_list = [row._mapping for row in result_table]
    return data_list


@router.post("/all_user_conversation")
@limiter.limit("100/second")
def list_all_users_conversation(
    request: Request,
    body: AdminListAllUserRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    conversation_management = ConversationManagement(db)
    result_table = conversation_management.show_all_conversation(
        page_size=body.page_size, page_number=body.page_number
    )
    data_list = [row._mapping for row in result_table]
    return data_list


@router.post("/create_character")
@limiter.limit("100/second")
def create_character(
    request: Request,
    body: AdminCreateCharacterRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    character_management = CharacterManagement(db)
    character = character_management.create_character(
        body.character_name, body.system_prompt
    )
    if not character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="角色创建失败！"
        )
    else:
        return {
            "msg": "角色创建成功！",
            "character_name": body.character_name,
            "character_id": character.id,
        }


@router.post("/delete_character")
@limiter.limit("100/second")
def delete_character(
    request: Request,
    body: AdminDeleteCharacterRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    character_management = CharacterManagement(db)
    if not character_management.delete_character(body.character_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="角色不存在！"
        )
    else:
        return {"msg": "角色删除成功！", "character_id": body.character_id}


@router.post("/get_chat_history")
@limiter.limit("100/second")
def admin_get_chat_history(
    request: Request,
    body: AdminGetChatHistoryRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    conversation_management = ConversationManagement(db)
    if not conversation_management.get_conversation(body.chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="对话不存在！"
        )
    return conversation_management.get_certain_history_chat(
        body.chat_id, page_size=body.page_size, page_number=body.page_number
    )


@router.post("/delete_conversation")
@limiter.limit("100/second")
def admin_delete_conversation(
    request: Request,
    body: AdminDeleteConversationRequest,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    conversation_management = ConversationManagement(db)
    if not conversation_management.get_conversation(body.chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="对话不存在！"
        )
    conversation_management.delete_conversation(body.chat_id)
    return {"msg": "删除成功！"}


@router.post("/get_softed_deleted_user")
@limiter.limit("100/second")
def get_softed_deleted_user(
    request: Request,
    body: AdminGetSoftDeletedUserRequest,
    create_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user_management = UserManagement(db)
    result_table = user_management.get_soft_deleted_users(
        page_size=body.page_size, page_number=body.page_number
    )
    data_list = [row._mapping for row in result_table]
    return data_list


@router.post("/get_not_allowed_words")
@limiter.limit("100/second")
def get_not_allowed_words(
    request: Request,
    body: AdminGetNotAllowedWordRequest,
    create_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    not_allowed_word_management = NotallowedWordManagement(db)
    result_table = not_allowed_word_management.get_not_allowed_words(
        page_size=body.page_size, page_number=body.page_number
    )
    data_list = [row._mapping for row in result_table]
    return data_list


@router.post("/add_not_allowed_word")
@limiter.limit("100/second")
def add_not_allowed_word(
    request: Request,
    body: AdminNotAllowedWordRequest,
    create_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    not_allowed_word_management = NotallowedWordManagement(db)
    if not not_allowed_word_management.create_not_allowed_word(body.word):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该单词已存在！"
        )
    else:
        return {"msg": "该单词已添加！", "word": body.word}


@router.post("/delete_not_allowed_word")
@limiter.limit("100/second")
def delete_not_allowed_word(
    request: Request,
    body: AdminNotAllowedWordRequestByID,
    create_user=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    not_allowed_word_management = NotallowedWordManagement(db)
    if not not_allowed_word_management.delete_not_allowed_word(
        body.not_allowed_word_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该单词不存在！"
        )
    else:
        return {"msg": "该单词已删除！"}
