from fastapi import APIRouter,Depends,HTTPException,status,Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.utils import get_db
from database.management import UserManagement
from schemas.user_schemas import UserRegisterRequest,UserLoginRequest
from security.security import SecurityUtils
from security.limit_request import limiter
from security.captcha import captcha_manager
from fastapi.responses import StreamingResponse
import io

router=APIRouter()

@router.get("/captcha")
@limiter.limit("60/minute")
def get_captcha(request: Request):
    """获取图形验证码"""
    data = captcha_manager.generate_captcha()
    # 返回图片流
    return StreamingResponse(
        data["image_data"], 
        media_type="image/png",
        headers={"X-Captcha-ID": data["captcha_id"]}
    )

@router.post("/register")
@limiter.limit("40/second")
def register_user(
    request: Request,
    user_data:UserRegisterRequest,
    db: Session=Depends(get_db)
):
    # 验证图形验证码
    if not captcha_manager.verify_captcha(user_data.captcha_id, user_data.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    user_mananger=UserManagement(db)
    password=SecurityUtils.get_password_hash(user_data.user_password)
    try:
        success=user_mananger.create_user(
            name=user_data.user_name,
            password=password
        )
        if success:
            user=user_mananger.get_user_by_name(user_data.user_name)
            return {
                "status":"ok",
                "msg":"注册成功",
                "user_id":user.user_id,
                "user_name":user_data.user_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="对不起，用户已经存在！"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册服务出错了！"
            )

@router.post("/login")
@limiter.limit("80/second")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session=Depends(get_db)
):
    user_mananger=UserManagement(db)
    user=user_mananger.get_user_by_name(form_data.username)
    user_password=form_data.password 
    if not user or user.is_deleted or not SecurityUtils.verify_password(user_password,hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="尊敬的用户您好，我们很抱歉的通知你，你所在的账号因存在违规行为，已被封禁，如有异议，请找管理员申诉，感谢您的配合。"
        )
    access_token=SecurityUtils.create_access_token(
        data={
            "sub":user.name,
            "user_id":user.user_id 
            },
    )        
    return {
            "access_token":access_token,
            "token_type": "bearer",
            "status":"ok",
            "msg":"登录成功！",
            "user_id":user.user_id,
            "user_name":user.name,
            }
    