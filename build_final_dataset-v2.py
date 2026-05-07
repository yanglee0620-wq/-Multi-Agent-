import os
import pandas as pd
import json
import random


def build_v2_dataset(weibo_csv_path, cnews_txt_path, old_json_path="test_dataset.json",
                     output_filename="test_dataset_v2.json"):
    final_dataset = []

    # ================= 0. 建立黑名单 =================
    used_texts = set()
    if os.path.exists(old_json_path):
        with open(old_json_path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            for item in old_data:
                used_texts.add(item['text'].strip())
        print(f"🛡️ 已加载 {len(used_texts)} 条历史数据作为黑名单。")

    # ================= 1. 提取 Weibo21 (假新闻) =================
    print(f"\n>>> 正在处理 Weibo21 数据集 ({weibo_csv_path})...")
    if os.path.exists(weibo_csv_path):
        df = pd.read_csv(weibo_csv_path, encoding='utf-8')

        # 兼容标签：匹配数字 1 或者文字 '谣言'
        fake_df = df[df['label'].astype(str).str.contains('1|谣言|不实|fake', na=False)]

        # 如果有领域区分，尽量选科技；如果没有，就全量挑
        if 'domain' in df.columns:
            fake_df = fake_df[
                fake_df['domain'].isin(['科技', 'Science', 'tech', 'technology', '财经商业', '科学', '数码'])]
        elif 'hashtag' in df.columns:
            fake_df = fake_df[fake_df['hashtag'].astype(str).str.contains('科技|科学|数码|手机')]

        new_fake_news = []
        for _, row in fake_df.iterrows():
            text = str(row['content']).strip()[:500]
            if text not in used_texts and len(text) > 50:
                new_fake_news.append(text)

        random.seed(2026)
        sampled_fake = random.sample(new_fake_news, min(50, len(new_fake_news)))

        for text in sampled_fake:
            final_dataset.append({"text": text, "true_label": 1})
        print(f"✅ 成功提取了 {len(sampled_fake)} 条全新科技谣言！")
    else:
        print(f"❌ 致命错误：找不到文件 {weibo_csv_path}！请检查文件名和路径。")

    # ================= 2. 提取 cnews (真新闻) =================
    print(f"\n>>> 正在处理 cnews 数据集 ({cnews_txt_path})...")
    if os.path.exists(cnews_txt_path):
        valid_tech_news = []
        with open(cnews_txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    label, content = parts[0], parts[1]
                    if label == '科技':
                        text = content[:500]
                        if text not in used_texts and len(text) > 50:
                            valid_tech_news.append(text)

        sampled_true = random.sample(valid_tech_news, min(50, len(valid_tech_news)))

        for text in sampled_true:
            final_dataset.append({"text": text, "true_label": 0})
        print(f"✅ 成功提取了 {len(sampled_true)} 条全新科技真新闻！")
    else:
        print(f"❌ 致命错误：找不到文件 {cnews_txt_path}！")

    # ================= 3. 打乱并保存 =================
    if len(final_dataset) == 100:
        random.shuffle(final_dataset)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_dataset, f, ensure_ascii=False, indent=4)
        print(f"\n🎉 完美！全新盲测集已保存至 {output_filename} (共 {len(final_dataset)} 条数据)")
    else:
        print(f"\n⚠️ 警告：当前数据总量为 {len(final_dataset)} 条，不是 100 条，请检查上面的报错信息！")


# 注意：如果你的数据集不在同一个文件夹，请在这里填入绝对路径，比如 'E:/桌面/weibo21.csv'
build_v2_dataset(
    weibo_csv_path="E:/桌面/TechNewsChecker/Chinese-FND-weibo21-main/Chinese-FND-weibo21-main/news.csv",
    cnews_txt_path="E:\桌面\TechNewsChecker\cnews\cnews.train.txt",
    old_json_path="test_dataset.json",
    output_filename="test_dataset_v2.json"
)