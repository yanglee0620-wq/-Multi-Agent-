import os
import pandas as pd
import json
import random


def build_mixed_tech_dataset(weibo_csv_path, cnews_txt_path, output_filename="test_dataset.json"):
    final_dataset = []

    # ================= 1. 提取 Weibo21 (微博谣言，保持不变) =================
    print(">>> 正在处理 Weibo21 数据集...")
    if os.path.exists(weibo_csv_path):
        df = pd.read_csv(weibo_csv_path, encoding='utf-8')
        domain_col = 'domain' if 'domain' in df.columns else 'hashtag'
        tech_df = df[df[domain_col].isin(['科技', 'Science', 'tech', 'technology', '财经商业'])]
        fake_tech_df = tech_df[tech_df['label'].astype(str).str.contains('谣言|不实', na=False)]

        sample_size = min(50, len(fake_tech_df))
        sampled_fake = fake_tech_df.sample(n=sample_size, random_state=42)

        for _, row in sampled_fake.iterrows():
            text = str(row['content']).strip()[:500]
            final_dataset.append({"text": text, "true_label": 1})
        print(f"✅ 成功从 Weibo21 提取了 {len(sampled_fake)} 条科技谣言！")
    else:
        print(f"⚠️ 找不到 Weibo21 文件：{weibo_csv_path}")

    # ================= 2. 提取 cnews 格式的纯正科技新闻 =================
    print("\n>>> 正在处理 cnews 训练集...")
    if os.path.exists(cnews_txt_path):
        valid_tech_news = []
        # 按行读取 txt 文件
        with open(cnews_txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 用 Tab 键 (\t) 把标签和正文切开
                parts = line.strip().split('\t')

                # 确保这一行格式正确，分成了两部分
                if len(parts) == 2:
                    label, content = parts[0], parts[1]

                    # 🎯 【最核心的绝杀】：只有官方标签明确写着“科技”的，我们才要！
                    if label == '科技':
                        valid_tech_news.append(content[:500])  # 截取前500字防大模型Token超限

        print(f"🔍 在该文件中共发现了 {len(valid_tech_news)} 篇官方盖章的科技新闻！")

        # 随机抽取 50 篇作为真新闻样本
        sample_size = min(50, len(valid_tech_news))
        sampled_true = random.sample(valid_tech_news, sample_size)

        for text in sampled_true:
            final_dataset.append({"text": text, "true_label": 0})

        print(f"✅ 成功提取了 {len(sampled_true)} 条100%纯正的科技真新闻！")
    else:
        print(f"⚠️ 找不到 cnews 文本文件：{cnews_txt_path}")

    # ================= 3. 打乱顺序并保存 =================
    if final_dataset:
        random.shuffle(final_dataset)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_dataset, f, ensure_ascii=False, indent=4)
        print(f"\n🎉 终极纯血科技盲测集构建完成！共 {len(final_dataset)} 条数据，已保存为 {output_filename}")


if __name__ == "__main__":
    # Weibo21 的路径
    WEIBO_CSV_FILE = r"E:\桌面\TechNewsChecker\Chinese-FND-weibo21-main\Chinese-FND-weibo21-main\mcfend\news.csv"

    # ⚠️【注意看这里】：把你新下载的 cnews.train.txt 的绝对路径填在这里！
    # 比如：r"E:\桌面\cnews\cnews.train.txt"
    CNEWS_TRAIN_FILE = r"E:\桌面\TechNewsChecker\cnews\cnews.train.txt"

    build_mixed_tech_dataset(WEIBO_CSV_FILE, CNEWS_TRAIN_FILE)