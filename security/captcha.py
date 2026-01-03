import random
import string
import uuid
import os
import redis
from captcha.image import ImageCaptcha
from dotenv import load_dotenv

load_dotenv()

class CaptchaManager:
    def __init__(self):
        self.image = ImageCaptcha(width=160, height=60)
        self.redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
        self.ttl = 300  # 5 minutes

    def generate_captcha(self) -> dict:
        """
        生成验证码
        :return: {"captcha_id": str, "image_base64": bytes}
        """
        # 1. 生成 4 位随机字符
        characters = string.digits + string.ascii_uppercase
        code = ''.join(random.choices(characters, k=4))
        
        # 2. 生成图片
        image_data = self.image.generate(code)
        image_data.seek(0)
        
        # 3. 生成 ID 并存入 Redis
        captcha_id = str(uuid.uuid4())
        key = f"captcha:{captcha_id}"
        
        # 存入 Redis (忽略大小写，存大写)
        self.redis_client.setex(key, self.ttl, code.upper())
        
        return {
            "captcha_id": captcha_id,
            "image_data": image_data  # Returns BytesIO object
        }

    def verify_captcha(self, captcha_id: str, code: str) -> bool:
        """
        验证验证码
        """
        if not captcha_id or not code:
            return False
            
        key = f"captcha:{captcha_id}"
        stored_code = self.redis_client.get(key)
        
        if not stored_code:
            return False
            
        # 验证一次即销毁 (防重放)
        self.redis_client.delete(key)
        
        return stored_code == code.upper()

captcha_manager = CaptchaManager()
