# app.py
import streamlit as st
import asyncio
import numpy as np
import plotly.graph_objects as go
from backend_api import evaluate_single_news  # 引入后端 API

st.set_page_config(page_title="多智能体科技新闻核查雷达", layout="wide", page_icon="🔬")

st.title("🔬 多智能体科技新闻置信度评估系统")
st.markdown("基于 `准确性`、`完整性`、`透明度` 11个维度的深度语义核查引擎 (V5 最终版)")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📝 输入新闻原文")
    news_input = st.text_area("请将长篇科技新闻复制到此处：", height=450, placeholder="在此处粘贴长文本（支持数千字）...")
    check_btn = st.button("🚀 一键多维核查")

with col2:
    st.subheader("📊 智能体体检报告单")
    if check_btn and news_input:
        with st.spinner('三大专家智能体正在运用思维链（CoT）并发审查中，请稍候...'):
            result = asyncio.run(evaluate_single_news(news_input))

            # 1. 判定结论看板
            score_percent = int(result["final_score"] * 100)
            if score_percent >= 60:
                st.success(f"### 综合置信度: {score_percent}分 \n {result['conclusion']}")
            elif score_percent >= 30:
                st.warning(f"### 综合置信度: {score_percent}分 \n {result['conclusion']}")
            else:
                st.error(f"### 综合置信度: {score_percent}分 \n {result['conclusion']}")

            # 提取维度名称和分数用于画图
            dim_names = ['1.1信源', '1.2数据', '1.3逻辑', '1.4炒作', '1.5幻觉',
                         '2.1周期', '2.2局限', '2.3替代', '3.1同行', '3.2利益', '3.3资金']

            scores = []
            scores.extend(list(result["dimensions"]["Accuracy"].values()))
            scores.extend(list(result["dimensions"]["Integrity"].values()))
            scores.extend(list(result["dimensions"]["Transparency"].values()))

            # 2. 动态生成可交互雷达图 (Plotly)
            if len(scores) == 11:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=scores + [scores[0]],  # 闭合雷达图
                    theta=dim_names + [dim_names[0]],
                    fill='toself',
                    name='本文得分',
                    line_color='#1f77b4' if score_percent >= 30 else '#d62728'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=False,
                    margin=dict(l=40, r=40, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            # 3. 致命硬伤标注 (智能体诊断评语)
            st.markdown("### 🩺 诊断评语与硬伤警告")
            
            # 准确性点评
            acc_analysis = result['diagnosis']['Accuracy_Analysis']
            if np.mean(list(result["dimensions"]["Accuracy"].values())) < 0.6:
                st.error(f"**【准确性一票否决】** {acc_analysis}")
            else:
                st.info(f"**【准确性点评】** {acc_analysis}")

            # 完整性点评
            int_analysis = result['diagnosis']['Integrity_Analysis']
            if np.mean(list(result["dimensions"]["Integrity"].values())) < 0.6:
                st.warning(f"**【完整性缺失】** {int_analysis}")
            else:
                st.info(f"**【完整性点评】** {int_analysis}")
                
            # 透明度点评
            tra_analysis = result['diagnosis']['Transparency_Analysis']
            if np.mean(list(result["dimensions"]["Transparency"].values())) < 0.5:
                st.warning(f"**【透明度存疑】** {tra_analysis}")
            else:
                st.info(f"**【透明度点评】** {tra_analysis}")
