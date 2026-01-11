from contextlib import asynccontextmanager
from database.utils import init_db
from database.engine_creating import engine,SessionLocal
from database.database_structure import User
from security.security import SecurityUtils

from fastapi import FastAPI,Request
from router import user_auth,user_conversation,admin
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import uvicorn
import os
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from security.limit_request import limiter

init_db(engine)
    
    # 初始化 Admin 用户
load_dotenv(verbose=True)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 启动时的逻辑
    # 初始化数据库表结构
    init_db(engine)
    
    # 初始化 Admin 用户
    load_dotenv(verbose=True)
    try:
        db: Session = SessionLocal()
        admin_name = os.environ.get("ADMIN_NAME")
        # 简单检查是否存在，如果不存在则创建（这里仅作简单示例，生产环境建议更严谨的判断）
        # 注意：这里需要从 database_structure 导入 User 模型，或者确保已有查询逻辑
        # 由于当前代码直接构造 User 对象，我们先尝试查询
        existing_admin = db.query(User).filter(User.name == admin_name).first()
        
        if not existing_admin and admin_name:
            print(f"Creating default admin user: {admin_name}")
            admin_user = User(
                name=admin_name,
                password=SecurityUtils.get_password_hash(os.environ.get("ADMIN_PASSWORD")),
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        db.close()
    except Exception as e:
        print(f"Initialization warning: {e}")
    # 初始化 Redis 缓存
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    print("FastAPI Cache initialized with Redis backend")
    
    yield
    # 2. 关闭时的逻辑 (如果是空则留空)
    await redis.close()
    print("Redis connection closed")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请改为具体的域名列表
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)
app.include_router(user_auth.router, prefix="/user_auth", tags=["用户管理接口"])
app.include_router(user_conversation.router, tags=["聊天相关"])
app.include_router(admin.router, prefix="/admin", tags=["管理员操作"])


@app.get("/",tags=["检查后端服务是否正常"])
@limiter.limit("120/minute")
def read_root(request:Request):
    return {
        "status":"OK"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)