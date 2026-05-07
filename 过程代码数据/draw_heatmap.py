# -*- coding: utf-8 -*-
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


def generate_heatmap(json_filepath):
    if not os.path.exists(json_filepath):
        print(f"❌ 找不到数据文件 {json_filepath}，请先运行 multi_agent.py 生成数据！")
        return

    # 1. 加载刚才跑出来的打分数据
    with open(json_filepath, "r", encoding="utf-8") as f:
        data_list = json.load(f)

    print(f"✅ 成功读取 {len(data_list)} 条有效深度核查数据，开始绘制热力图...")

    # 2. 转为 Pandas DataFrame
    df = pd.DataFrame(data_list)

    # 3. 计算皮尔逊相关系数矩阵 (Pearson Correlation)
    corr_matrix = df.corr(method='pearson')

    # 4. 设置中文字体（防止乱码）
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows用SimHei，Mac用黑体
    plt.rcParams['axes.unicode_minus'] = False

    # 5. 开始画高颜值热力图
    plt.figure(figsize=(11, 9))

    # 使用 seaborn 画图，cmap选择酷炫的红蓝渐变
    ax = sns.heatmap(
        corr_matrix,
        annot=True,  # 显示具体数字
        cmap='coolwarm',  # 颜色风格 (蓝色代表负相关，红色代表正相关)
        vmin=0, vmax=1,  # 分数都是正向打分，通常呈正相关，范围设为0到1更清晰
        square=True,  # 保证每个格子是正方形
        linewidths=.5,  # 格子之间的白线宽度
        fmt='.2f',  # 保留两位小数
        annot_kws={"size": 12}  # 字体大小
    )

    # 调整标签角度，看起来更专业
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)

    plt.title('多智能体 7 大评估维度相关性分析 (Pearson Correlation)', size=16, pad=20, weight='bold')
    plt.tight_layout()

    # 6. 保存图片
    save_path = "Dimension_Correlation_Heatmap.png"
    plt.savefig(save_path, dpi=300)
    print(f"🎉 热力图生成成功！已保存为高清图片: {save_path}")

    # 展示出来给你看
    plt.show()


if __name__ == "__main__":
    generate_heatmap("agent_scores_for_heatmap.json")