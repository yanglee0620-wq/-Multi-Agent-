#生成科技新闻置信度评估维度-相关性热力图
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 假设这是你跑完大模型后收集到的数据表
# 每一列是一个细分维度，最后一列是真实的基准标签 (true_label: 0=真新闻, 1=假新闻/谣言)
# 你需要修改这里的文件路径为你实际生成的评估结果文件
data_path = "E:\桌面\TechNewsChecker\维度相关性原始数据_0414_0946.csv"

try:
    df = pd.read_csv(data_path)

    # 提取所有的细分维度列（例如 "1.1 信源权威度", "2.1 研发周期" 等）
    # 假设你的 df 中包含了名为 1.1, 1.2 ... 3.3 的列以及 true_label 列
    dimensions = [col for col in df.columns if col != 'true_label' and col != 'text']

    print("正在计算各维度与【新闻真实性】的相关性...\n")

    # 计算每个维度与 true_label 的皮尔逊相关系数
    correlations = {}
    for dim in dimensions:
        # 注意：这里计算的是该维度的得分与 true_label 的相关性。
        # 正常情况下，你的 Agent 打分越高（越严谨/越完整），它是假新闻（true_label=1）的概率就越低。
        # 所以出来的相关系数通常是负数。负得越多，说明这个维度越能有效识别谣言！
        corr = df[dim].corr(df['true_label'])
        correlations[dim] = corr

    # 排序并格式化输出
    sorted_corr = sorted(correlations.items(), key=lambda x: x[1])

    print("=== 细分维度有效性排行榜（负相关性越强，鉴别效果越好） ===")
    for dim, corr in sorted_corr:
        print(f"维度 {dim}: {corr:.4f}")

    # 如果你想给领导看图表，可以取消下面代码的注释，直接生成热力图
    '''
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 解决中文显示问题
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[dimensions + ['true_label']].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("科技新闻置信度评估维度 - 相关性热力图")
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png")
    print("热力图已生成: correlation_heatmap.png")
    '''

except FileNotFoundError:
    print(f"请先将 Agent 的跑分结果保存为 {data_path}。")