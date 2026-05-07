import os
import json

# 这是从你的截图中提取出来的绝对路径
# 注意：如果你的实际路径有变，请修改这里
folder_path = r"E:\桌面\TechNewsChecker\Chinese_Rumor_Dataset-master\Chinese_Rumor_Dataset-master\CED_Dataset\original-microblog"

print("正在从数据集抽取原始新闻文本...\n")

# 我们只遍历前 20 个文件看看长什么样
files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

for filename in files[:20]:
    file_path = os.path.join(folder_path, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 提取微博的正文内容
            text = data.get("text", "未找到正文")
            print(f"【文件 {filename}】:\n{text}\n")
            print("-" * 50)
    except Exception as e:
        print(f"读取 {filename} 时出错: {e}")