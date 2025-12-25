from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    session_id: str  # 会话 ID
    message: str     # 用户的问题
    file: Optional[str] = None  # 可选字段，存储文件的路径或文件信息，如果用户上传文件则设置

class ChatResponse(BaseModel):
    reply: str       # AI 的回答
    session_id: str  # 会话 ID