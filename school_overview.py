# -*- coding: utf-8 -*-

import streamlit as st

# ###########################################################################
# #页面样式
def load_css():
    st.markdown("""
    <style>
    /* --- 全局设置 --- */
    .main {
        background-color: #F9FAFB;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- 1. 徽章区域优化 (状态区分) --- */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 1.5rem;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.8rem;
        border-radius: 50px; /* 胶囊形状 */
        font-size: 0.8rem;
        font-weight: 600;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    /* True 状态：柔和绿底 + 深绿字 + 浅绿边框 */
    .b-yes { 
        background-color: #ECFDF5; 
        color: #047857; 
        border-color: #A7F3D0;
    }
    
    /* False 状态：浅灰底 + 灰字 + 极淡边框 */
    .b-no { 
        background-color: #F3F4F6; 
        color: #9CA3AF; 
        border-color: #E5E7EB;
    }

    /* --- 2. 核心指标卡片 (瘦身版) --- */
    .metric-card {
        padding: 1rem 1.2rem; /* 减小内边距：原 1.8rem 1rem */
        border-radius: 10px;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04); /* 减小阴影 */
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }

    /* 颜色风格定义 (保持之前的渐变) */
    .style-blue { background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%); color: #FFFFFF; }
    .style-purple { background: linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%); color: #FFFFFF; }
    .style-warm { background: linear-gradient(135deg, #FBBF77 0%, #F59E0B 100%); color: #FFFFFF; }

    .val-lg {
        font-size: 1.8rem; /* 减小字号：原 2.5rem */
        font-weight: 800;
        line-height: 1.2;
        font-variant-numeric: tabular-nums;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .val-unit {
        font-size: 0.9rem; /* 减小单位字号 */
        opacity: 0.9;
        font-weight: 500;
    }

    .lbl-metric {
        font-size: 0.7rem; /* 减小标签字号 */
        margin-top: 0.4rem; /* 减小间距 */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.9;
    }

    /* --- 3. 详细数据 (保持不变) --- */
    .detail-col-wrapper { padding: 0 1rem; }
    @media (min-width: 768px) {
        .detail-col-wrapper:not(:first-child) { border-left: 1px solid #E5E7EB; }
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.7rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .detail-row:last-child { border-bottom: none; }

    .lbl-detail { font-size: 0.85rem; color: #6B7280; font-weight: 500; flex-shrink: 0; margin-right: 1rem; }
    .val-detail { font-size: 0.95rem; font-weight: 700; color: #1F2937; text-align: right; flex-grow: 1; }
    </style>
    """, unsafe_allow_html=True)

# ###########################################################################
# #页面布局与填充数据
def load_layout(data):
    # 1. 头部：徽章 (动态类名)
    # 定义徽章生成逻辑
    def get_badge_html(is_true, label):
        cls = "b-yes" if is_true else "b-no"
        icon = "✓" if is_true else "×"
        return f'<span class="badge {cls}">{icon} {label}</span>'

    b_985 = get_badge_html(data['F985'], "985工程")
    b_211 = get_badge_html(data['F211'], "211工程")
    b_dual = get_badge_html(data['双一流'], "双一流")

    st.markdown(f"""
    <div class="badge-container">
        {b_985}{b_211}{b_dual}
    </div>
    """, unsafe_allow_html=True)

    # 2. 核心指标 (瘦身卡片)
    m_col1, m_col2, m_col3 = st.columns(3)
    
    def get_metric_html(val, unit, label, style_class):
        return f"""
        <div class="metric-card {style_class}">
            <div class="val-lg">{val}<span class="val-unit">{unit}</span></div>
            <div class="lbl-metric">{label}</div>
        </div>
        """

    with m_col1:
        st.markdown(get_metric_html(data['软科排名'], "", "软科排名", "style-blue"), unsafe_allow_html=True)
    with m_col2:
        st.markdown(get_metric_html(data['保研率'], "%", "保研率", "style-purple"), unsafe_allow_html=True)
    with m_col3:
        st.markdown(get_metric_html(data['创建时间'], "年", "建校时间", "style-warm"), unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. 详细数据
    d_col1, d_col2, d_col3 = st.columns(3, gap="large")

    def get_detail_item(label, value):
        return f"""<div class="detail-row">
            <span class="lbl-detail">{label}</span>
            <span class="val-detail">{value}</span>
        </div>"""

    def wrap_detail_col(content):
        return f'<div class="detail-col-wrapper">{content}</div>'

    with d_col1:
        content = get_detail_item("所在省份", data['省份']) + get_detail_item("所在城市", data['城市'])
        st.markdown(wrap_detail_col(content), unsafe_allow_html=True)

    with d_col2:
        content = get_detail_item("办学体制", data['办学体制']) + get_detail_item("办学层次", data['办学层次'])
        st.markdown(wrap_detail_col(content), unsafe_allow_html=True)

    with d_col3:
        content = get_detail_item("办学类型", data['办学类型']) + get_detail_item("隶属关系", data['隶属关系'])
        st.markdown(wrap_detail_col(content), unsafe_allow_html=True)
    
    st.space()
    st.space()

if __name__ == '__main__':
    # 设置全局页面样式
    st.set_page_config(
        page_title="高校档案",
        page_icon="🏫", layout="wide",
        initial_sidebar_state="collapsed"
    )
    