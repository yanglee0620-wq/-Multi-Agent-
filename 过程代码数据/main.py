# -*- coding: utf-8 -*-
import json
from openai import OpenAI

# ================= 1. 配置你的模型 =================
# 将这里的字符串替换为你实际的 API Key 和 Base URL
API_KEY = "c9382ed87a70407989966e251df993c6.SwMeOMk30tPrTZSH"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL_NAME = "glm-4-flash"  # 例如 "gpt-4o", "deepseek-chat", "glm-4"

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


# ================= 2. 定义核心逻辑 =================
def check_news_credibility(news_text):
    """
    调用大模型，严格依据七大维度核查科技新闻可信度
    """
    print("正在呼叫大模型进行七大维度深度核查，请稍候...\n")

    # 这里直接使用了文档中要求的“单智能体判断提示词”
    system_prompt = """
    请你作为科技新闻可信度核查AI，严格依据以下七大核心维度，全面分析目标科技新闻文本，输出可信度评级（高/中/低/不可信）、各维度核查结果及核心依据，禁止遗漏任一维度，判断需贴合维度内“可信/可疑特征”，不主观臆断：
    1. 信源维度：核查信源资质、溯源能力及发布者专业性，确认是否可追溯至一级信源（科研机构、顶刊等），是否标注原始出处；
    2. 科学表述维度：核查表述是否严谨、无绝对化，是否明确技术阶段，不混淆实验室原型与量产、动物实验与人体临床等，不包含伪科学表述；
    3. 证据维度：核查新闻是否有完整实证支撑（样本量、实验参数等），结论是否经同行评议、可重复，不虚构数据；
    4. 新闻伦理维度：核查报道是否中立平衡，是否披露利益关联，不歪曲、不断章取义，无明显营销导向；
    5. 逻辑维度：核查文本逻辑是否自洽、无跳跃，不混淆相关性与因果性，结论符合基础科学常识；
    6. 核查维度：核查新闻是否可通过多方权威信源交叉验证，时间线是否真实，无旧闻新炒情况；
    7. AI生成内容维度：核查新闻是否为AI代写编造，有无署名、采访细节等人工核查痕迹，信源、术语、细节是否自洽。

    输出格式为：
    可信度评级（高/中/低/不可信）
    各维度分析（简要列出7个维度的判定依据）
    核心风险点（若评级为中、低、不可信时则输出）。
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请核查以下科技新闻的可信度：\n\n{news_text}"}
            ],
            temperature=0.1  # 保持较低的温度，让模型输出更客观、严谨
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"请求模型时发生错误：{e}"


# ================= 3. 运行测试 =================
if __name__ == "__main__":
    # 待测试的“伪科学”新闻样本
    test_news = """
        【重磅开源】硅谷初创团队 NextMind 今日在 GitHub 平台开源了号称“全球首个无限逼近 AGI（通用人工智能）”的大模型项目 Omega-X。据其官方 README 文档宣称，该模型在多项内部逻辑推理测试中智商超越人类专家，不仅能自主修复系统架构级 Bug，甚至能根据一句话需求从零编写全新操作系统。官方强调，Omega-X 将彻底颠覆现有软件工程生命周期，预计3年内将替代全球80%的初高中级程序员。
        然而，有眼尖的开发者发现，该 GitHub 仓库目前仅提供了一份充斥着华丽图表的 PDF 技术白皮书和几段精美的预渲染演示视频，最核心的模型权重文件（Weights）和训练代码并未真正公开，仅提供了一个需要付费排队的 API 接口。尽管如此，该项目依靠各种营销通稿，在短短24小时内已狂刷超 5 万颗 Star，引发科技圈剧烈震荡，多位不具名投资人表示已准备跟进A轮融资。
        """

    print("--- 待核查新闻 ---")
    print(test_news.strip() + "\n")
    print("--- 开始分析 ---")

    result = check_news_credibility(test_news)

    print(result)
