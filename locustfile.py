"""
Locust 压力测试脚本
针对 CyreneSimulator API 进行压测
"""
from locust import HttpUser, task, between
import json


class CyreneUser(HttpUser):
    """模拟普通用户行为"""
    wait_time = between(1, 3)  # 每次请求间隔 1-3 秒
    token = None
    user_id = None
    
    def on_start(self):
        """用户启动时先登录获取 token"""
        # 使用测试账号登录
        response = self.client.post(
            "/user_auth/login",
            data={
                "username": "test_user",
                "password": "test123456"
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user_id")
        else:
            # 如果登录失败，尝试注册
            self.client.post(
                "/user_auth/register",
                json={
                    "user_name": "test_user",
                    "user_password": "test123456"
                }
            )
            # 再次登录
            response = self.client.post(
                "/user_auth/login",
                data={
                    "username": "test_user",
                    "password": "test123456"
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
    
    @property
    def auth_headers(self):
        """获取认证头"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(3)
    def get_characters(self):
        """获取角色列表 - 高频操作"""
        self.client.post(
            "/get_character_name",
            json={"page_size": 10, "page_number": 1},
            headers=self.auth_headers
        )
    
    @task(2)
    def get_conversations(self):
        """获取对话列表"""
        self.client.post(
            "/get_current_user_conversation",
            json={"page_size": 10, "page_number": 1},
            headers=self.auth_headers
        )
    
    @task(1)
    def get_chat_history(self):
        """获取聊天历史"""
        self.client.post(
            "/get_chat_history",
            json={"chat_id": 1},
            headers=self.auth_headers
        )


class LoginStressUser(HttpUser):
    """专门压测登录接口"""
    wait_time = between(0.5, 1)
    
    @task
    def login_test(self):
        """登录压测"""
        self.client.post(
            "/user_auth/login",
            data={
                "username": "test_user",
                "password": "test123456"
            }
        )
