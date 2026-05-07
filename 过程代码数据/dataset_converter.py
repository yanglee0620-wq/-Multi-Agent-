import json
import pandas as pd
import os


def convert_to_system_format(input_file, output_file="large_test_dataset.json"):
    """
    将外部下载的开源数据集（CSV/Excel）转换为多智能体系统支持的 JSON 格式
    """
    print(f"正在读取原始数据集: {input_file}...")

    # 假设你下载的是 CSV 格式（如果是 Excel 就用 pd.read_excel）
    # 注意：你需要根据实际下载的数据集，修改下方的列名！
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        # 假设微博数据集里，新闻内容的列名叫 'content'，标签的列名叫 'label' (0代表真，1代表假)
        text_column = 'content'
        label_column = 'label'

        # 提取并清洗数据
        df = df[[text_column, label_column]].dropna()  # 丢弃空数据

        # 转换为系统需要的字典列表格式
        formatted_data = []
        for index, row in df.iterrows():
            # 限制文本长度，防止超长文本浪费太多 Token (截取前500字)
            cleaned_text = str(row[text_column]).strip()[:500]
            label = int(row[label_column])

            formatted_data.append({
                "text": cleaned_text,
                "true_label": label
            })

        # 写入 JSON 文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)

        print(f"✅ 转换成功！共转换了 {len(formatted_data)} 条数据。")
        print(f"📁 文件已保存为: {output_file}")

    except Exception as e:
        print(f"❌ 转换失败，请检查文件路径或列名是否正确。报错信息: {e}")


if __name__ == "__main__":
    # 使用示例：
    # 1. 把你下载的 Weibo21_dataset.csv 放在同级目录
    # 2. 修改上方的 text_column 和 label_column 为实际的表头名字
    # 3. 运行这个脚本！

    # 这里你需要替换为你实际下载的文件名
    INPUT_FILE = "Weibo21_dataset.csv"

    # 如果文件存在，就执行转换
    if os.path.exists(INPUT_FILE):
        convert_to_system_format(INPUT_FILE)
    else:
        print(f"⚠️ 找不到文件 {INPUT_FILE}，请先去 GitHub 下载数据集并放到本目录下哦！")