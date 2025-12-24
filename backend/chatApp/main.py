from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uuid
from io import BytesIO
import PyPDF2  # 用于PDF解析

from schemas.chat import ChatRequest, ChatResponse
from services.llm_service import ChatSession

app = FastAPI(title="PKU Intelligence API")

# -----------------------------
# CORS 中间件（自动处理 OPTIONS）
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许所有的前端域名
    allow_credentials=True,
    allow_methods=["*"],      # 允许所有方法
    allow_headers=["*"],      # 允许所有头部
)

sessions: Dict[str, ChatSession] = {}
pdf_contents: Dict[str, str] = {}  # 存储每个会话的 PDF 文本内容

@app.post("/upload_pdf", response_model=ChatResponse)
async def upload_pdf(file: UploadFile = File(...), session_id: str = ""):
    """ 上传 PDF 文件并将其内容解析为文本 """
    
    # 如果没有传递 session_id，自动生成一个新的会话 ID
    if not session_id:
        session_id = str(uuid.uuid4())  # 生成一个唯一的 session_id
    
    # 确保会话存在
    if session_id not in sessions:
        sessions[session_id] = ChatSession("你是一个由北京大学团队开发的智能助手，名叫 PKU Intelligence。")
    
    session = sessions[session_id]

    try:
        # 读取上传的 PDF 文件
        pdf_reader = PyPDF2.PdfReader(BytesIO(await file.read()))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()

        # 保存 PDF 内容到会话
        pdf_contents[session_id] = text

        # 返回文件上传成功的响应，确保返回有效的 session_id
        #return ChatResponse(reply="PDF 文件已成功上传并解析，请提出您的问题。", session_id=session_id)
        return ChatResponse(reply=f"PDF 文件已成功上传并解析，请提出您的问题。会话 ID: {session_id}",session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 处理失败: {str(e)}")


@app.post("/ask_question", response_model=ChatResponse)
async def ask_question(req: ChatRequest):
    """ 提出问题并基于上传的 PDF 内容进行回答 """
    
    # 确保会话存在
    if req.session_id not in sessions:
        raise HTTPException(status_code=4001, detail="会话不存在，请先上传 PDF 文件。")
    
    session = sessions[req.session_id]

    # 获取对应会话的 PDF 内容
    if req.session_id not in pdf_contents:
        raise HTTPException(status_code=4002, detail="未找到与该会话相关的 PDF 文件。请先上传 PDF 文件。")
    
    pdf_text = pdf_contents[req.session_id]

    try:
        # 使用 PDF 文本和用户问题进行交互
        ai_reply = session.chat(f"请根据以下内容回答问题：\n{pdf_text}\n问题：{req.message}")
        return ChatResponse(reply=ai_reply, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")


@app.get("/")
async def root():
    return {"status": "backend running"}