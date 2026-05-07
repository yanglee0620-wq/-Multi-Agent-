import asyncio
import numpy as np
from backend_api import evaluate_single_news

# ================= 准备“多极态”对抗测试集 =================
# 我们精心设计了 4 种截然不同的文风，用来刺探系统的泛化底线
TEST_CASES = {
    "1. 纯学术摘要 (硬核/严谨/客观)": """
    近期，《自然》杂志发表了MIT团队的最新研究。研究人员开发了一种新型固态电池电解质，在室温下离子电导率达到了10^-3 S/cm。该研究在小鼠模型和初步纽扣电池测试中，循环500次后容量保持率达85%。作者指出，尽管目前在大规模制造上仍面临成本过高的局限性，且距离商业化还有至少5年时间，但该成果为下一代储能设备提供了新的理论支撑。
    """,

    "2. 商业公关通稿 (夸大/报喜不报忧)": """
    重磅！星辰科技公司今日震撼发布全球首款“全宇宙最强”AI芯片！算力吊打所有友商1000倍！只要插上这块芯片，你的电脑就能拥有自主意识！发布会上，公司CEO宣布该产品即将全面量产，预购价仅需9998元！目前尚未看到任何第三方跑分数据，但行业专家表示，这绝对是颠覆人类历史的伟大发明，友商已经彻底颤抖了！
    """,

    "3. 伪科学/微商软文 (造谣/常识错误/强行缝合)": """
    惊呆了！某隐世老中医结合最新的量子纠缠理论，研发出了“量子石墨烯护颈仪”。不用打针不用吃药，只要戴上它，里面的一亿个量子机器人就会顺着经络打通血管，不仅能彻底治愈多年的颈椎病，还能发射特殊波长消灭体内的游离癌细胞。目前该产品已经获得某神秘风投的10亿注资。现在拨打电话，原价一万的护颈仪只要99元！
    """,

    "4. 数码产品评测 (常规/中性/无同行评议)": """
    今天我们拿到了最新款的 XYZ 智能手机。经过实际测试，在室温25度下，运行大型游戏半小时，机身最高温度为42度，帧率稳定在58帧左右。相比上一代，电池容量提升了10%，但快充协议依然只支持私有协议。总体来说，这是一次中规中矩的常规升级，没有太多颠覆性的黑科技，是否值得购买取决于你目前手持的设备型号。
    """
}


async def run_adversarial_test():
    print("🚀 开始执行多极态自动化对抗测试...\n")

    for case_name, content in TEST_CASES.items():
        print(f"==========================================")
        print(f"▶️ 正在测试类别: {case_name}")
        print(f"📝 文本前瞻: {content[:40].strip()}...")
        print("⏳ 智能体分析中...")

        try:
            # 越过网页端，直接调用我们底层的核心 API
            result = await evaluate_single_news(content)

            # 计算并提取各维度的平均分 (转成百分制方便查看)
            final_score = result.get("final_score", 0) * 100
            acc_score = np.mean(list(result["dimensions"]["Accuracy"].values())) * 100
            int_score = np.mean(list(result["dimensions"]["Integrity"].values())) * 100
            tra_score = np.mean(list(result["dimensions"]["Transparency"].values())) * 100

            print(f"📊 【综合置信度】: {final_score:.1f}分 | 结论: {result['conclusion']}")
            print(f"   ├─ 准确性均分: {acc_score:.1f} (考核: 信源/数据/逻辑/防炒作/幻觉)")
            print(f"   ├─ 完整性均分: {int_score:.1f} (考核: 研发周期/局限性/替代方案)")
            print(f"   └─ 透明度均分: {tra_score:.1f} (考核: 同行评议/利益冲突/资金)")

            print(f"🩺 【AI 核心诊断截取】:")
            print(f"   - 准确性点评: {result['diagnosis'].get('Accuracy_Analysis', '无')}")
            print(f"   - 完整性点评: {result['diagnosis'].get('Integrity_Analysis', '无')}")

        except Exception as e:
            print(f"❌ 测试失败: {e}")

        print(f"==========================================\n")


if __name__ == "__main__":
    # Windows 环境下运行 asyncio 可能会报错，加这一行保平安
    import sys

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_adversarial_test())