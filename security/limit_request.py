import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from dotenv import load_dotenv
import os


# 1. 你的自定义 Key 函数
def get_rate_limit_key(request: Request):
    # 优先获取真实 IP
    forwarded = request.headers.get("X-Forwarded-For")
    print(
        f"DEBUG LIMITER: remote={request.client.host}, x-forwarded-for={forwarded}",
        flush=True,
    )
    if forwarded:
        real_ip = forwarded.split(",")[0]
    else:
        real_ip = get_remote_address(request)

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            # 仅解码，不验证签名，追求速度
            payload = jwt.decode(token, options={"verify_signature": False})
            return str(payload.get("user_id", real_ip))
        except:
            pass
    return real_ip


# 2. 初始化 Limiter 实例
# 这个实例会被 main.py 和各个 router 引用
load_dotenv()
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
# swallow_errors=False 方便调试连接问题，生产环境可改为 True
limiter = Limiter(
    key_func=get_rate_limit_key, storage_uri=redis_url, swallow_errors=False
)
