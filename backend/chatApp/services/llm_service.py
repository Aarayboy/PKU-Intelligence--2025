from typing import List, Dict
from openai import OpenAI
from ..core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_llm_api(messages: List[Dict[str, str]]) -> str:
    """调用 OpenAI LLM API 来生成回复"""
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
        self.pdf_content = ""  # 用来存储 PDF 文件的内容

    def add(self, role: str, content: str):
        """将消息添加到会话内存"""
        self.memory.append({"role": role, "content": content})

    def set_pdf_content(self, pdf_text: str):
        """设置 PDF 文件的内容"""
        self.pdf_content = pdf_text
        # 将 PDF 内容作为系统消息添加到会话内存中
        self.add("system", f"以下是上传的 PDF 内容：\n{self.pdf_content}")

    def chat(self, user_input: str) -> str:
        """与用户进行对话，并基于 PDF 内容生成回答"""
        # 将用户输入添加到对话内存
        self.add("user", user_input)
        
        # 调用 LLM API 获取回答
        reply = call_llm_api(self.memory)
        
        # 将 AI 的回复添加到内存
        self.add("assistant", reply)
        
        return reply