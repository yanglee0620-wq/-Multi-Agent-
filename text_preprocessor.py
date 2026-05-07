import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="sk-cf2076b10c894f07934c869421770aaa",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ================= 策略1：智能截断器 =================
def smart_truncate(text, max_length=2500):
    """
    智能截断：应对动辄万字的超长文本，防止直接崩掉大模型。
    采用首尾保留法（保留前 70% 和后 30%）
    """
    if len(text) <= max_length:
        return text

    print(f"⚠️ 触发超长文本截断：原长 {len(text)} 字，正在进行首尾压缩...")
    keep_front = int(max_length * 0.7)
    keep_back = int(max_length * 0.3)

    truncated_text = text[:keep_front] + "\n\n...[此处省略冗长中间细节]...\n\n" + text[-keep_back:]
    return truncated_text


# ================= 策略2：要素提纯器 =================
async def extract_core_elements(safe_text):
    """
    使用大模型将长新闻降维，提取核心评估要素。
    """
    extraction_prompt = """你是一个专业的科技新闻编辑。
    请将下面这篇科技新闻压缩提纯，剥离抒情和冗余描述，仅输出以下三个结构化要素。
    如果原文缺失某项，请直接写“未提及”。总字数严格控制在 300 字以内。

    【输出格式要求】
    1. 核心技术主旨：(一句话总结它宣称的技术突破)
    2. 关键数据与证据：(列出文中的具体数字、实验结果、有效率等)
    3. 提及的机构与信源：(列出背书的大学、公司、期刊、专家名字)
    """

    try:
        response = await client.chat.completions.create(
            model="qwen-plus",  # 提取要素任务简单，可以用稍微轻量/便宜的模型
            messages=[
                {"role": "system", "content": "严格按照指定格式提取要素，不要输出任何额外废话。"},
                # 策略3：指令后置！把长文本放在前面，把要求放在后面，防止大模型遗忘
                {"role": "user", "content": f"【新闻原文】\n{safe_text}\n\n【任务】\n{extraction_prompt}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"要素提取失败，降级处理。错误信息: {str(e)}"


# ================= 主入口：预处理管道 =================
async def run_preprocessing_pipeline(raw_long_text):
    """
    对外部输入的不可控长文本进行全流程清洗与准备
    """
    # 1. 物理防御：斩断超限文本
    safe_text = smart_truncate(raw_long_text, max_length=3000)

    # 2. 信息降维：提纯核心要素
    core_elements = await extract_core_elements(safe_text)

    # 3. 组装终极 Context，喂给后续的三大专家 Agent
    # 专家 Agent 不再阅读万字长文，而是阅读这个结构化的高密度摘要，外加部分原文
    final_context_for_agents = f"""
    === 【系统提取的新闻核心要素】 ===
    {core_elements}

    === 【新闻原文参考片段】 ===
    {safe_text[:1000]} # 仅附带前1000字原文供 Agent 感受语言风格(用于判断炒作/机翻痕迹)
    """

    return final_context_for_agents


# ================= 测试运行 =================
if __name__ == "__main__":
    # 模拟一篇极长的假新闻（复制粘贴大量废话）
    dummy_long_news = "震惊！斯坦福大学宣布攻克癌症！" + "详情请看..." * 1000 + "这项技术耗资500万，有效率99%。"


    async def test():
        processed_context = await run_preprocessing_pipeline(dummy_long_news)
        print("====== 最终喂给三大专家的黄金上下文 ======")
        print(processed_context)


    asyncio.run(test())