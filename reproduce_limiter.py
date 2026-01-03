import requests
import time

URL = "http://localhost:8000/user_auth/login"
# 如果在 Docker 中且端口映射了，或者直接运行 Python

def test_limit():
    print(f"Testing Rate Limit on {URL}")
    for i in range(1, 16):
        try:
            # 改为发送 data (Form Data) 以匹配 OAuth2PasswordRequestForm
            response = requests.post(URL, data={"username": "test", "password": "pwd"})
            print(f"Request {i}: Status {response.status_code}")
            if response.status_code == 429:
                print("Rate Limit Triggered! (Success)")
                return
        except Exception as e:
            print(f"Request {i} failed: {e}")
        # time.sleep(0.1) 

    print("Rate Limit NOT Triggered (Failure)")

if __name__ == "__main__":
    test_limit()
