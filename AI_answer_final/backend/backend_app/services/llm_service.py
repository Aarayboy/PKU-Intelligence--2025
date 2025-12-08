from typing import List, Dict
from openai import OpenAI
from ..core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

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