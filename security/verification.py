from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from database.utils import get_db
from .security import SecurityUtils,SECRET_KEY,ALGORITHM
from database.management import UserManagement

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="user_auth/login")

async def get_current_user(
        token:str=Depends(oauth2_scheme),
        db:Session=Depends(get_db)
        ):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload=jwt.decode(
            token=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id:int=payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_manager=UserManagement(db)
    user=user_manager.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    if user.is_deleted or user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户状态异常"
        )
    return user

async def get_current_admin(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return current_user