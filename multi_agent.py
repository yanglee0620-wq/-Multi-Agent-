# -*- coding: utf-8 -*-
import os
import json
import datetime
import asyncio
import time
import warnings
import sys
import numpy as np
import pandas as pd
from openai import AsyncOpenAI
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 彻底解决 Windows 下 Event loop is closed 的报错
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ================= 1. 基础配置 =================
warnings.filterwarnings("ignore")

client = AsyncOpenAI(
    api_key="sk-cf2076b10c894f07934c869421770aaa",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    max_retries=2
)

# 🚀 提速修改 1：解除并发封印，将同时请求数提升至 50
API_SEMAPHORE = asyncio.Semaphore(30)

# ================= 2. 核心维度智能体配置 =================
agents_config = {
    "AccuracyAgent": {
        "role": "准确性核查专家",
        "model": "qwen-plus",
        "prompt": """你负责评估科技新闻的【准确性】。请严格根据以下二级维度进行实战检验：
1.1 信源权威度：首发信源是否为顶刊/机构/知名学者？
1.2 数据严谨性：是否有数值支撑？样本量是否符合常识？
1.3 逻辑合理性：是否将“相关性”夸大为“因果性”？
1.4 炒作免疫力：是否滥用绝对化/情绪化词汇？
1.5 AI/机翻痕迹：是否存在AI编造的不存在文献或机构（幻觉）？

【核心指令：思维链优先】
1. 识别语境：区分“严肃学术/医学”与“数码产品评测”。
2. 打分参考(Few-Shot)：若为普通数码科技新闻，只要数据真实、逻辑无硬伤，基础分应默认给到 0.7~0.9，严禁因其无学术背景就打低分。若为伪科学（如量子治癌），直接打 0.1。
3. 一票否决(防漏网漏洞)：即便被判定为普通数码资讯，一旦发现以下任意一点：①信源完全匿名且无测试条件；②使用违背常识的极端夸张词(如“秒杀一切”、“全宇宙最强”)；③无实体验证的伪科学概念拼凑。必须触发一票否决，该维度分数强行打 0.1~0.2，绝不姑息无实质依据的软文！

你必须且只能输出一个 JSON，严格遵守以下字段顺序：
1. "analysis": "一针见血指出核心逻辑或硬伤（必须控制在20字以内）。"
2. "scores": {"1.1": 数字, "1.2": 数字, "1.3": 数字, "1.4": 数字, "1.5": 数字}"""
    },
    "IntegrityAgent": {
        "role": "完整性核查专家",
        "model": "qwen-plus",
        "prompt": """你负责评估科技新闻的【完整性】。请严格根据以下二级维度进行实战检验：
2.1 研发阶段定位：是否清晰标明了研究阶段？
2.2 风险与局限披露：报道是否提及了副作用、成本或目前的硬伤？
2.3 竞争方案对比：是否提及了解决同一问题的其他技术路线？

【核心指令：思维链优先】
1. 识别语境：区分“严肃学术/医学”与“数码产品评测”。
2. 打分参考(Few-Shot)：若为普通数码科技新闻，只要数据真实、逻辑无硬伤，基础分应默认给到 0.7~0.9，严禁因其无学术背景就打低分。若为伪科学（如量子治癌），直接打 0.1。
3. 一票否决(防漏网漏洞)：即便被判定为普通数码资讯，一旦发现以下任意一点：①信源完全匿名且无测试条件；②使用违背常识的极端夸张词(如“秒杀一切”、“全宇宙最强”)；③无实体验证的伪科学概念拼凑。必须触发一票否决，该维度分数强行打 0.1~0.2，绝不姑息无实质依据的软文！

你必须且只能输出一个 JSON，严格遵守以下字段顺序：
1. "analysis": "一针见血指出核心逻辑或硬伤（必须控制在20字以内）。"
2. "scores": {"2.1": 数字, "2.2": 数字, "2.3": 数字}"""
    },
    "TransparencyAgent": {
        "role": "透明度核查专家",
        "model": "qwen-plus",
        "prompt": """你负责评估科技新闻的【透明度】。请严格根据以下二级维度进行实战检验：
3.1 同行评议背书：该突破是否已发表在同行评议期刊上？
3.2 利益冲突披露：报道是否暗示了背后的商业利益或软广倾向？
3.3 资金透明度：是否明确提及了研究的资助方？

【核心指令：思维链优先】
1. 识别语境：区分“严肃学术/医学”与“数码产品评测”。
2. 打分参考(Few-Shot)：若为普通数码科技新闻，只要数据真实、逻辑无硬伤，基础分应默认给到 0.7~0.9，严禁因其无学术背景就打低分。若为伪科学（如量子治癌），直接打 0.1。
3. 一票否决(防漏网漏洞)：即便被判定为普通数码资讯，一旦发现以下任意一点：①信源完全匿名且无测试条件；②使用违背常识的极端夸张词(如“秒杀一切”、“全宇宙最强”)；③无实体验证的伪科学概念拼凑。必须触发一票否决，该维度分数强行打 0.1~0.2，绝不姑息无实质依据的软文！

你必须且只能输出一个 JSON，严格遵守以下字段顺序：
1. "analysis": "一针见血指出核心逻辑或硬伤（必须控制在30字以内）。"
2. "scores": {"3.1": 数字, "3.2": 数字, "3.3": 数字}"""
    }
}


# ================= 3. 核心处理函数 =================
async def run_expert_agent(agent_name, news_text):
    config = agents_config[agent_name]
    async with API_SEMAPHORE:
        try:
            response = await client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": "你是一个执行 CoT 倒置逻辑的 JSON 机器。不要输出任何 Markdown 标签。"},
                    {"role": "user", "content": f"{config['prompt']}\n\n待核查原文：\n{news_text[:1500]}"}
                ],
                temperature=0.1
            )
            raw_content = response.choices[0].message.content.strip()
            import re
            raw_content = re.sub(r"^```json", "", raw_content, flags=re.MULTILINE)
            raw_content = re.sub(r"```$", "", raw_content, flags=re.MULTILINE)
            return json.loads(raw_content.strip())
        except Exception as e:
            return {"scores": {}, "error": str(e), "analysis": f"节点超时或解析失败"}


async def process_news_item(item, index, report_file, results_list):
    news_text = item['text']
    true_label = item['true_label']

    start_time = time.time()

    tasks = [run_expert_agent(name, news_text) for name in agents_config.keys()]
    results = await asyncio.gather(*tasks)

    acc_res, int_res, tra_res = results

    all_scores = {}
    all_scores.update(acc_res.get("scores", {}))
    all_scores.update(int_res.get("scores", {}))
    all_scores.update(tra_res.get("scores", {}))

    acc_avg = np.mean(list(acc_res.get("scores", {}).values())) if acc_res.get("scores") else 0.2
    int_avg = np.mean(list(int_res.get("scores", {}).values())) if int_res.get("scores") else 0.2
    tra_avg = np.mean(list(tra_res.get("scores", {}).values())) if tra_res.get("scores") else 0.2

    # 🎯 全局泛化权重：(0.4, 0.4, 0.2)
    # 逻辑：均衡准确性与完整性，保留基础透明度考核，防止对单一维度过拟合
    final_score = (acc_avg * 0.4) + (int_avg * 0.4) + (tra_avg * 0.2)

    # 🎯 全局泛化及格线：0.25 (黄金分割点)
    # 逻辑：给真实的商业新闻留下充足的容错空间，同时将 0.1~0.2 分的纯伪科学死死按在水下
    pred_label = 1 if final_score < 0.30 else 0

    elapsed = time.time() - start_time

    record = {
        "index": index,
        "true_label": true_label,
        "pred_label": pred_label,
        "final_confidence": final_score
    }
    record.update(all_scores)
    results_list.append(record)

    status = "✅ 正确" if pred_label == true_label else "❌ 错误"
    report_file.write(f"\n样本 {index} ({elapsed:.2f}s) | 真实:{true_label} 预测:{pred_label} | {status}\n")
    report_file.write(
        f"指标得分: 准确性:{acc_avg:.2f} | 完整性:{int_avg:.2f} | 透明度:{tra_avg:.2f} | 总分:{final_score:.2f}\n")
    report_file.write(f"准确性分析: {acc_res.get('analysis', 'N/A')}\n")

    return pred_label


# ================= 4. 主循环 =================
async def main():
    with open("test_dataset_v2.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    timestamp = datetime.datetime.now().strftime("%m%d_%H%M")
    report_name = f"科技新闻质量评估报告_{timestamp}.txt"
    csv_name = f"维度相关性原始数据_{timestamp}.csv"

    y_true = [item['true_label'] for item in dataset]
    y_pred = []
    results_list = []

    print(f"🚀 开始评估 {len(dataset)} 条科技新闻 (已开启极速模式)...")

    with open(report_name, "w", encoding="utf-8") as rf:
        rf.write("========== 科技新闻置信度评估系统 (满分极速版V5) ==========\n\n")

        for i, item in enumerate(dataset):
            pred = await process_news_item(item, i + 1, rf, results_list)
            y_pred.append(pred)
            if (i + 1) % 10 == 0:
                print(f"⚡ 已极速处理 {i + 1} 条...")

        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        rf.write("\n" + "=" * 50 + "\n")
        rf.write("系统最终指标汇总:\n")
        rf.write(f"🎯 准确率 (Accuracy) : {acc:.4f}\n")
        rf.write(f"🎯 精确率 (Precision): {prec:.4f}\n")
        rf.write(f"🎯 召回率 (Recall)   : {rec:.4f}\n")
        rf.write(f"🎯 综合得分 (F1)     : {f1:.4f}\n")

    df = pd.DataFrame(results_list)
    df.to_csv(csv_name, index=False, encoding='utf-8-sig')

    print(f"\n✅ 极速评估完成！\n报告已生成：{report_name}\n相关性数据已导出：{csv_name}")


if __name__ == "__main__":
    asyncio.run(main())