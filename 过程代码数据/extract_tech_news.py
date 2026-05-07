import pandas as pd
import json
import os


def build_pure_tech_dataset(csv_filepath, output_filename="test_dataset.json"):
    """
    从带有领域标签的开源数据集中，定向抽取带有“科技”标签的数据
    """
    if not os.path.exists(csv_filepath):
        print(f"❌ 找不到文件：{csv_filepath}，请先检查路径！")
        return

    print(f"正在读取原始数据集 {csv_filepath} ...")
    try:
        # 读取下载的开源数据集
        df = pd.read_csv(csv_filepath, encoding='utf-8')

        # 1. 填坑：Weibo21 把领域标签错写在了 'hashtag' 这一列
        domain_col = 'domain' if 'domain' in df.columns else 'hashtag'

        # 过滤出科技领域
        tech_df = df[df[domain_col].isin(['科技', 'Science', 'tech', 'technology'])]

        print(f"🔍 成功在数据集中找到了 {len(tech_df)} 条带有明确【科技】标签的新闻！")

        formatted_data = []
        for index, row in tech_df.iterrows():
            text = str(row['content']).strip()[:500]  # 截取前500字防Token超限

            # 2. 填坑：将中文的“谣言/事实”转换为咱们系统需要的 1 和 0
            label_str = str(row['label']).strip()
            # 如果包含谣言/假/不实，则打标为 1，否则为 0 (真新闻)
            label = 1 if '谣言' in label_str or '不实' in label_str else 0

            formatted_data.append({
                "text": text,
                "true_label": label
            })

        # 导出为你系统直接能用的 test_dataset.json
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)

        print(f"✅ 纯科技类测试集已生成：{output_filename}，可以直接用 multi_agent.py 跑了！")

    except Exception as e:
        print(f"❌ 处理出错，请检查错误提示: {e}")


if __name__ == "__main__":
    # 使用原始字符串处理 Windows 路径
    build_pure_tech_dataset(
        r"E:\桌面\TechNewsChecker\Chinese-FND-weibo21-main\Chinese-FND-weibo21-main\mcfend\news.csv")