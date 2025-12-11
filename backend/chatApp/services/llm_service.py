from typing import List, Dict
from openai import OpenAI
from ..core.config import settings

# 使用 config 中计算好的 API_KEY 和 BASE_URL
import httpx

# 逻辑优化：
# 1. 如果是 DashScope (阿里云)，使用 trust_env=False 忽略系统代理，强制直连。
#    这解决了 "proxies" 参数在某些 httpx 版本中报错的问题，同时达到了禁用代理的效果。
# 2. 如果是 OpenAI，使用默认的 httpx.Client()，它会自动读取系统环境变量 (HTTP_PROXY, HTTPS_PROXY)。
#    用户只需在 .env 中配置 HTTP_PROXY=http://127.0.0.1:your_port 即可生效。

if "dashscope" in (settings.BASE_URL or ""):
    http_client = httpx.Client(trust_env=False)
else:
    http_client = httpx.Client()

client = OpenAI(
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL,
    http_client=http_client
)

def call_llm_api(messages: List[Dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content


class ChatSession:
    """独立管理一个聊天会话"""
    def __init__(self, system_prompt: str):
        self.memory = [{"role": "system", "content": system_prompt}]

    def add(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})

    def chat(self, user_input: str) -> str:
        self.add("user", user_input)
        reply = call_llm_api(self.memory)
        self.add("assistant", reply)
        return reply