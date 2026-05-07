# backend_api.py
import streamlit as st
import asyncio
import json
import re
import numpy as np
from openai import AsyncOpenAI
import os

# 使用 Streamlit 的安全密钥机制读取 Key，或者使用环境变量（兼容本地测试）
api_key = os.getenv("QWEN_API_KEY", "sk-cf2076b10c894f07934c869421770aaa")
try:
    if "QWEN_API_KEY" in st.secrets:
        api_key = st.secrets["QWEN_API_KEY"]
except:
    pass

client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

async def preprocess_news(long_text):
    prompt = """你是一个科技情报提取器。请将下面这篇长篇科技新闻浓缩为以下三个要素（总字数不超过300字）：
    1. 核心主旨：
    2. 引用的核心数据：
    3. 提及的机构与信源："""
    try:
        safe_text = long_text[:3000]
        response = await client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你只负责提取客观要素，不进行评价。"},
                {"role": "user", "content": f"【待处理原文】\n{safe_text}\n\n【任务】\n{prompt}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception:
        return "预处理提取失败，降级使用原文截断。"

async def call_expert_agent(agent_name, news_context):
    if "Accuracy" in agent_name:
        keys = '{"1.1": 数字, "1.2": 数字, "1.3": 数字, "1.4": 数字, "1.5": 数字}'
    elif "Integrity" in agent_name:
        keys = '{"2.1": 数字, "2.2": 数字, "2.3": 数字}'
    else:
        keys = '{"3.1": 数字, "3.2": 数字, "3.3": 数字}'

    prompt = f"""你是一个冷酷、理性的科技新闻核查专家。

    【核心指令：思维链优先】
    1. 识别语境：优先判断文本是“严肃学术/前沿科学”还是“消费级数码/商业公关稿”。
    2. 打分基准(Few-Shot)：若为消费级数码资讯，只要评测数据真实、逻辑无硬伤，即便没有顶刊背书，各维度基础分也应默认给到 0.7~0.9。
    3. 一票否决界限(极度重要)：你必须严格区分【商业营销修辞】与【伪科学常识错误】。
       - 赦免条件：允许数码公关稿使用适度的夸张修辞（如“性能怪兽”、“秒杀前代”），这属于常规商业行为，绝不可因此触发一票否决！
       - 击杀条件：仅当发现以下致命硬伤时触发一票否决（该维度强制打0.1分）：① 违背基础物理/医学常识（如“老鼠测电池”、“量子纠缠治病”）；② 信源机构被证实为AI捏造的幻觉；③ 毫无实证的绝症攻克声明。

    【任务要求】
    你必须且只能输出一个 JSON 字符串，严格遵守以下字段顺序：
    1. "analysis": "一针见血指出核心逻辑或硬伤（必须控制在30字以内）。"
    2. "scores": {keys} (范围0.0~1.0)

    待核查内容：
    {news_context}
    """

    try:
        response = await client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个执行 CoT 倒置逻辑的 JSON 机器。不要输出任何 Markdown 标签。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        raw_content = response.choices[0].message.content.strip()
        raw_content = re.sub(r"^```json", "", raw_content, flags=re.MULTILINE)
        raw_content = re.sub(r"```$", "", raw_content, flags=re.MULTILINE)
        return json.loads(raw_content.strip())
    except Exception as e:
        fallback = {"1.1": 0.2, "1.2": 0.2, "1.3": 0.2, "1.4": 0.2, "1.5": 0.2} if "Accuracy" in agent_name else {"2.1": 0.2, "2.2": 0.2, "2.3": 0.2}
        return {"scores": fallback, "analysis": f"节点超时或解析失败"}

async def evaluate_single_news(news_text):
    summary = await preprocess_news(news_text)
    context = f"【要素提纯】\n{summary}\n\n【原文精华】\n{news_text[:1500]}"

    tasks = [
        call_expert_agent("Accuracy", context),
        call_expert_agent("Integrity", context),
        call_expert_agent("Transparency", context)
    ]
    results = await asyncio.gather(*tasks)
    acc_res, int_res, tra_res = results

    acc_scores = list(acc_res.get("scores", {}).values())
    int_scores = list(int_res.get("scores", {}).values())
    tra_scores = list(tra_res.get("scores", {}).values())

    avg_acc = np.mean(acc_scores) if acc_scores else 0.2
    avg_int = np.mean(int_scores) if int_scores else 0.2
    avg_tra = np.mean(tra_scores) if tra_scores else 0.2

    # 🎯 全局泛化权重：(0.4, 0.4, 0.2)
    final_score = (avg_acc * 0.4) + (avg_int * 0.4) + (avg_tra * 0.2)

    # 🎯 全局泛化及格线：0.30
    if final_score >= 0.60:
        conclusion = "✅ 极高置信度 (硬核科技/真实可信资讯)"
    elif final_score >= 0.30:
        conclusion = "⚠️ 存疑/夸大 (建议交叉核实关键数据，或包含营销水分)"
    else:
        conclusion = "❌ 高危谣言/伪科学 (严重缺乏实证支撑或违背常识)"

    return {
        "final_score": final_score,
        "conclusion": conclusion,
        "dimensions": {
            "Accuracy": acc_res.get("scores", {}),
            "Integrity": int_res.get("scores", {}),
            "Transparency": tra_res.get("scores", {})
        },
        "diagnosis": {
            "Accuracy_Analysis": acc_res.get("analysis", ""),
            "Integrity_Analysis": int_res.get("analysis", ""),
            "Transparency_Analysis": tra_res.get("analysis", "")
        }
    }
