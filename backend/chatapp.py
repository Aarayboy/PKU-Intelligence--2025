from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict

from chatApp.schemas.chat import ChatRequest, ChatResponse
from chatApp.services.llm_service import ChatSession

app = FastAPI(title="PKU Intelligence API")

# -----------------------------
# CORS 中间件（自动处理 OPTIONS）
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 建议生产环境写成特定域名
    allow_credentials=True,
    allow_methods=["*"],      # 允许所有方法
    allow_headers=["*"],      # 允许所有头部
)

sessions: Dict[str, ChatSession] = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    print(f"Received message: {req.message} in session: {req.session_id}")
    if req.session_id not in sessions:
        sessions[req.session_id] = ChatSession(
            "你是一个由北京大学团队开发的智能助手，名叫 PKU Intelligence。"
        )

    session = sessions[req.session_id]

    try:
        ai_reply = session.chat(req.message)
        return ChatResponse(reply=ai_reply, session_id=req.session_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"status": "backend running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)