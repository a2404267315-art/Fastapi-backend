from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    user_name: str = Field(
        ..., min_length=2, max_length=50, description="用户名 (2-50字符)"
    )
    user_password: str = Field(..., min_length=8, description="用户密码 (最少8位)")
    captcha_id: str = Field(..., description="验证码 ID")
    captcha_code: str = Field(..., description="验证码内容")


class UserLoginRequest(BaseModel):
    user_name: str
    user_password: str
