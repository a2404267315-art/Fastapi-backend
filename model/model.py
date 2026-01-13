from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)


class CyreneLLMModel:
    def __init__(
        self, client=None, system_prompt=None, history_chat=None, model=None
    ):  # 初始化客户端
        self.client = client
        self.system_prompt = system_prompt
        self.history_chat = history_chat if history_chat is not None else []
        self.model = model

    def chatting(
        self, contents: str, model="deepseek-chat", temperature=1.0, max_tokens=8192
    ):
        system_prompt = [{"role": "system", "content": self.system_prompt}]
        current_msg = [{"role": "user", "content": contents}]
        message_request_head = system_prompt + self.history_chat + current_msg
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=message_request_head,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            def stream_generator():
                full_text = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        yield chunk.choices[0].delta.content
                self.history_chat.append({"role": "user", "content": contents})
                self.history_chat.append({"role": "assistant", "content": full_text})

            return stream_generator()
        except Exception as e:
            raise ValueError(f"api调用错误{e}")

    @classmethod
    def create_dialog(
        cls,
        system_prompt,
        api_key=None,
        base_url=None,
        model: str = "deepseek-chat",
        history_chat=None,
    ):
        client = OpenAI(
            api_key=os.environ.get("API_KEY") or api_key,
            base_url=os.environ.get("BASE_URL") or base_url,
        )
        return cls(client, system_prompt, history_chat, model)
