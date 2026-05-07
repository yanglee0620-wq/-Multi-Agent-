#生成多维能力雷达图与相关性热力图 (V5终极版)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 设置中文显示（Windows 默认黑体）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_ppt_charts(csv_file="维度相关性原始数据_0417_1048.csv"):
    if not os.path.exists(csv_file):
        print(f"❌ 找不到文件 {csv_file}，请确保文件名正确！")
        return

    print(f"📊 正在读取最终跑批数据: {csv_file}...")
    df = pd.read_csv(csv_file)

    # 提取 11 个细分维度的列名
    dims = ['1.1', '1.2', '1.3', '1.4', '1.5', '2.1', '2.2', '2.3', '3.1', '3.2', '3.3']
    dim_names = ['1.1 信源', '1.2 数据', '1.3 逻辑', '1.4 炒作', '1.5 幻觉',
                 '2.1 周期', '2.2 局限', '2.3 替代', '3.1 同行', '3.2 利益', '3.3 资金']

    # ================= 1. 维度相关性热力图 =================
    plt.figure(figsize=(10, 8))
    corr_cols = ['true_label'] + dims
    corr_matrix = df[corr_cols].corr()

    # 替换坐标轴名称，让 PPT 更好看
    corr_matrix.columns = ['真实标签(假新闻=1)'] + dim_names
    corr_matrix.index = ['真实标签(假新闻=1)'] + dim_names

    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title("科技新闻置信度评估维度 - 相关性热力图 (基于V5终极测试集)", fontsize=16, pad=15)
    plt.tight_layout()
    plt.savefig("PPT用图_相关性热力图.png", dpi=300)
    print("✅ 已生成：PPT用图_相关性热力图.png")
    plt.close()

    # ================= 2. 多维能力雷达图 =================
    # 计算真假新闻在各个维度的平均分
    mean_true = df[df['true_label'] == 0][dims].mean().values.tolist()
    mean_fake = df[df['true_label'] == 1][dims].mean().values.tolist()

    # 雷达图需要闭合路径（首尾相连）
    mean_true += mean_true[:1]
    mean_fake += mean_fake[:1]
    angles = [n / float(len(dims)) * 2 * np.pi for n in range(len(dims))]
    angles += angles[:1]

    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    # 绘制真新闻（蓝色系，分数应偏高）
    ax.plot(angles, mean_true, linewidth=2, linestyle='solid', label='真新闻 (均分)', color='#1f77b4')
    ax.fill(angles, mean_true, '#1f77b4', alpha=0.2)

    # 绘制假新闻（红色系，分数应极低）
    ax.plot(angles, mean_fake, linewidth=2, linestyle='solid', label='假新闻/谣言 (均分)', color='#d62728')
    ax.fill(angles, mean_fake, '#d62728', alpha=0.2)

    # 设置刻度和标签
    plt.xticks(angles[:-1], dim_names, size=11)
    ax.set_rlabel_position(30)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=10)
    plt.ylim(0, 1.0)

    plt.title("多维能力雷达图 (真假新闻群体特征对比)", size=16, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.tight_layout()
    plt.savefig("PPT用图_多维能力雷达图.png", dpi=300)
    print("✅ 已生成：PPT用图_多维能力雷达图.png")
    plt.close()

if __name__ == "__main__":
    create_ppt_charts()
