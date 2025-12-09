import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    API_KEY: str = OPENAI_API_KEY if OPENAI_API_KEY else DASHSCOPE_API_KEY
    # DashScope 兼容 OpenAI 接口的 Base URL 通常是 https://dashscope.aliyuncs.com/compatible-mode/v1
    BASE_URL: str = "https://api.openai.com/v1" if OPENAI_API_KEY else "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # 通义千问模型名称通常为 qwen-turbo, qwen-plus, qwen-max
    MODEL_NAME: str = "gpt-4-turbo" if os.getenv("OPENAI_API_KEY") else "qwen-turbo"
    
    # 代理设置 (仅用于 OpenAI)
    PROXY_URL: str = os.getenv("PROXY_URL") or os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")

settings = Settings()   

# DEBUG INFO
print(f"DEBUG: Loaded API_KEY: {settings.API_KEY[:8]}... (Length: {len(settings.API_KEY)})")
print(f"DEBUG: Loaded BASE_URL: {settings.BASE_URL}")
print(f"DEBUG: Loaded MODEL_NAME: {settings.MODEL_NAME}")
print(f"DEBUG: Loaded PROXY_URL: {settings.PROXY_URL}")