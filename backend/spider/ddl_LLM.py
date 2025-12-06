import os
import json
from dataclasses import dataclass
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, timezone
import asyncio  # 新增：用于并发调用 LLM
from spider.ddl_spider import collect_all_assignment_texts

# ======================= LLM 配置部分 =======================

@dataclass
class LLMConfig:
    model_name: str
    api_key: str
    api_endpoint: str
    api_version: str = ""
    temperature: float = 0.3
    max_tokens: int = 4000


def get_llm_config() -> LLMConfig:
    env_path = Path(__file__).resolve().parent / ".env"  # 不管从哪儿 python app.py，都会加载和这个文件同目录下的 .env
    load_dotenv(env_path)
    api_key = os.getenv("QWEN_API_KEY")
    model_name = os.getenv("QWEN_MODEL_NAME")
    api_endpoint = os.getenv("QWEN_BASE_URL")

    # 创建 LLM 配置
    llm_config = LLMConfig(
        model_name=model_name,
        api_key=api_key,
        api_endpoint=api_endpoint,
        api_version="",
        temperature=0.5,    # 降低随机性以获得更稳定的输出
        max_tokens=4000,    # 确保响应足够长
    )
    return llm_config


# ======================= 调用 LLM 的底层函数（单次调用） =======================

def call_llm_for_deadlines(raw_items: List[Dict[str, str]],
                           llm_config: LLMConfig) -> Dict[str, Any]:
    """
    输入：
        raw_items: 由 ddl_spider.collect_all_assignment_texts(session) 返回的列表，
                   每条形如 {"课程名称": ..., "名称": ..., "细则": ...}

    输出：
        一个 dict:
        {
          "deadlines": [
            { "name": "...", "deadline": "YYYY-MM-DD HH:MM", "message": "...", "status": 0/1 },
            ...
          ]
        }
    """

    # 0) 计算当前北京时间字符串
    beijing_tz = timezone(timedelta(hours=8))
    beijing_now = datetime.now(beijing_tz)
    beijing_now_str = beijing_now.strftime("%Y-%m-%d %H:%M")

    # 1) 拼原始条目，方便 LLM 理解
    lines = []
    for idx, item in enumerate(raw_items, start=1):
        course_name = item.get("课程名称", "")
        name = item.get("名称", "")
        detail = item.get("细则", "")
        lines.append(f"[{idx}] 课程：{course_name}\n名称：{name}\n细则：{detail}")
    raw_block = "\n\n".join(lines)

    # 2) prompt
    system_prompt = (
        "你是一个帮助整理课程作业与DDL的助手。\n"
        f"当前时间（北京时间）是：{beijing_now_str}。\n"
        "你将看到若干原始条目，每条包含：课程名称、名称（作业名）、细则（包含截止时间说明等）。\n"
        "你的任务是：提取清洗后的任务列表，统一输出为 JSON 对象，键名为 \"deadlines\"，"
        "对应一个数组，每个元素必须包含以下字段：\n"
        "  - name: 任务名称（优先用条目中的“名称”，必要时可稍作精简，如果单看“名称”看不出是哪一门课程的，你需要加上课程名称）。\n"
        "  - deadline: 截止时间，统一格式为 \"YYYY-MM-DD HH:MM\"（24小时制），"
        "    如果无法确定具体时间，填 null。\n"
        "  - message: 对任务的简短说明，可以直接使用“细则”或提炼一两句话，语言要玩最近的梗，要有意思。"
        "    如果截止日期临近，你可以加上催促完成的话语，注意基于当前北京时间进行判断。\n"
        "  - status: 0 或 1。约定 0 表示紧急（比如距离现在很近 / 截止时间已过或即将到期），"
        "    1 表示不紧急。如果无法判断，请默认 1。\n"
        "要求：\n"
        "  - 只输出一个 JSON 对象，键名必须是 \"deadlines\"，对应一个数组。\n"
        "  - 不要输出任何额外解释、注释或多余文本。\n"
        "  - 合理去重：同一个作业如果重复出现，只保留一条即可。\n"
    )

    user_prompt = (
        "下面是从教学平台爬取到的原始作业条目，请你按照上述要求进行清洗、解析并输出 JSON：\n\n"
        f"{raw_block}\n\n"
        "请只返回 JSON 对象，例如：\n"
        "{\n"
        "  \"deadlines\": [\n"
        "    { \"name\": \"作业1\", \"deadline\": \"2025-12-01 23:59\", \"message\": \"完成第3章\", \"status\": 0 },\n"
        "    { \"name\": \"Project Milestone\", \"deadline\": \"2025-12-15 12:00\", \"message\": \"提交原型\", \"status\": 1 }\n"
        "  ]\n"
        "}\n"
    )

    headers = {
        "Authorization": f"Bearer {llm_config.api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": llm_config.model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": llm_config.temperature,
        "max_tokens": llm_config.max_tokens,
    }

    base_url = llm_config.api_endpoint.rstrip("/")
    url = f"{base_url}/chat/completions"
    print("DEBUG LLM URL:", url)

    resp = requests.post(url, headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"LLM 返回结构异常: {data}") from e

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 返回的内容不是合法 JSON: {content}") from e

    if "deadlines" not in parsed or not isinstance(parsed["deadlines"], list):
        raise ValueError(f"LLM 返回 JSON 中缺少 'deadlines' 字段: {parsed}")

    return parsed


# ======================= 并发调用相关的辅助函数 =======================

def _chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """把列表按固定大小切片，比如 chunk_size=2 时：[0,1],[2,3],[4,5]..."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def _call_llm_for_deadlines_async(raw_items: List[Dict[str, str]],
                                        llm_config: LLMConfig) -> Dict[str, Any]:
    """
    异步包装：把原来的同步 call_llm_for_deadlines 丢进线程池，
    这样不会阻塞事件循环，适合并发执行。
    """
    return await asyncio.to_thread(call_llm_for_deadlines, raw_items, llm_config)


async def _clean_deadlines_concurrently(raw_items: List[Dict[str, str]],
                                        llm_config: LLMConfig,
                                        chunk_size: int = 2) -> List[Dict[str, Any]]:
    """
    核心：把 raw_items 每 chunk_size 条切一块，并发调用 LLM 清洗，
    最后把所有块的 deadlines 拼接成一个大列表，顺序无所谓。
    """
    chunks = _chunk_list(raw_items, chunk_size)
    if not chunks:
        return []

    print(f"总共有 {len(raw_items)} 条原始作业记录，将被切分为 {len(chunks)} 个块（每块 {chunk_size} 条）。")

    # 为每个块创建一个协程任务
    tasks = [
        _call_llm_for_deadlines_async(chunk, llm_config)
        for chunk in chunks
    ]

    # 并发执行所有块的 LLM 调用
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_deadlines: List[Dict[str, Any]] = []

    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            print(f"[WARN] 第 {idx} 个块调用 LLM 失败：{res}")
            continue

        deadlines = res.get("deadlines", [])
        if not isinstance(deadlines, list):
            print(f"[WARN] 第 {idx} 个块返回的结构中 'deadlines' 字段不是列表：{res}")
            continue

        all_deadlines.extend(deadlines)

    print(f"并发清洗完成，总共汇总得到 {len(all_deadlines)} 条 deadlines。")
    return all_deadlines


# ======================= 最终暴露给外部的主函数 =======================

def build_deadline_payload_with_llm(session, user_id: str) -> Dict[str, Any]:
    """
    高层封装函数：
      1. 使用 ddl_spider.collect_all_assignment_texts(session) 爬取所有课程作业原始信息
      2. 把 raw_items 每两条切一块，多个协程并发调用 LLM 清洗为结构化的 deadlines 列表
      3. 构造最终要发送给 /edit/deadline 的 JSON Body:

         {
           "UserId": "1",
           "deadlines": [
             { "name": "...", "deadline": "...", "message": "...", "status": 0 },
             ...
           ]
         }

    返回上述 dict。
    """
    # 1) 爬虫获取原始条目（同步）
    raw_items = collect_all_assignment_texts(session)
    if not raw_items:
        # 没有任何作业，返回空结构
        return {
            "UserId": str(user_id),
            "deadlines": [],
        }

    # 2) 加载 LLM 配置
    llm_config = get_llm_config()

    # 3) 使用协程并发，每两条一块调用一次 LLM
    #    注意：这里使用 asyncio.run 包一层，这个函数本身仍然是同步接口
    deadlines = asyncio.run(
        _clean_deadlines_concurrently(raw_items, llm_config, chunk_size=2)
    )

    # 4) 拼出最终要 POST 的 Body
    payload = {
        "UserId": str(user_id),
        "deadlines": deadlines,
    }
    print("===== HERE is the 😋 payload ! =====")
    print(payload)
    return payload