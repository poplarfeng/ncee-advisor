# -*- coding: utf-8 -*-

# 导入标准模块
import base64
from pathlib import Path

# 导入第三方模块
import streamlit as st
import pandas as pd


# ##########################################################################
# 参数与常量设置
# ##########################################################################

# #-------------------------------------------------------------------------
# 1.dataframe数据省份信息与geojson地理文件省份信息映射
PROVINCE_NAME_MAPPING = {
    '河南': '河南省', 
    '浙江': '浙江省',
    '海南': '海南省', 
    '台湾': '台湾省', 
    '甘肃': '甘肃省', 
    '湖北': '湖北省',
    '天津': '天津市', 
    '内蒙古': '内蒙古自治区', 
    '广西': '广西壮族自治区', 
    '江苏': '江苏省',
    '山东': '山东省', 
    '北京': '北京市', 
    '西藏': '西藏自治区', 
    '青海': '青海省',
    '重庆': '重庆市', 
    '澳门': '澳门特别行政区', 
    '吉林': '吉林省',
    '福建': '福建省', 
    '广东': '广东省', 
    '上海': '上海市', 
    '江西': '江西省', 
    '香港': '香港特别行政区', 
    '黑龙江': '黑龙江省', 
    '山西': '山西省', 
    '云南': '云南省', 
    '四川': '四川省', ''
    '安徽': '安徽省', 
    '宁夏': '宁夏回族自治区', 
    '辽宁': '辽宁省', 
    '湖南': '湖南省', 
    '陕西': '陕西省', 
    '河北': '河北省', ''
    '新疆': '新疆维吾尔自治区', 
    '贵州': '贵州省',
    '境界线': '境界线'
}

# 2.省份与地域对应关系
PROVINCE_TO_REGION = {
  "华北地区": ["北京市", "天津市", "河北省", "山西省", "内蒙古自治区"],
  "东北地区": ["辽宁省", "吉林省", "黑龙江省"],
  "华东地区": ["上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省"],
  "华中地区": ["河南省", "湖北省", "湖南省"],
  "华南地区": ["广东省", "广西壮族自治区", "海南省"],
  "西南地区": ["重庆市", "四川省", "贵州省", "云南省", "西藏自治区"],
  "西北地区": ["陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区"],
  "港澳台地区": ["香港特别行政区", "澳门特别行政区", "台湾省"]
}

# 3.历年广东省高考特殊控制线
CONTROL_LINE = {'2021': 539, '2022': 538, '2023': 539, '2024':532, '2025': 534}

# 4.志愿填报智能推荐参数
RECOMMEND_RANK_PARAMS = {
    'rank': {'safe': [0.05, 0.1], 'target': [-0.05, 0.05], 'challenge': [-0.1, -0.05]},
    'score': {'safe': [-15, -10], 'target': [-10, 10], 'challenge': [10, 15]}
}




# ##########################################################################
#  streamlit组件样式设置
# ##########################################################################

# #-------------------------------------------------------------------------
# 1. st.divider分隔线样式设置,主要缩小分隔线上下边距
def set_divider_style():
    st.markdown(
    """
    <style>
        /* ========== 分割线统一样式 (适配 st.divider 和 markdown) ========== */
        
        /* 1. 针对 st.divider() 生成的 div 容器 */
        div.stDivider hr {
            margin-top: 0.5rem !important;
            margin-bottom: 1.0rem !important;
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, #667eea, #764ba2, #667eea, transparent) !important;
            border-radius: 2px !important;
            position: relative;
            overflow: hidden;
        }

        /* 2. 针对 st.markdown("---") 生成的原生 hr */
        hr {
            margin-top: 0.5rem !important;
            margin-bottom: 1.0rem !important;
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, #667eea, #764ba2, #667eea, transparent) !important;
            border-radius: 2px !important;
            position: relative;
            overflow: hidden;
        }
        
        /* 3. 流动光效动画 */
        div.stDivider hr::after,
        hr::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        /* 4. 侧边栏微调 */
        .stSidebar div.stDivider hr,
        .stSidebar hr {
            margin-top: 0.3rem !important;
            margin-bottom: 0.8rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# #-------------------------------------------------------------------------
# 2. st.popover样式设置,主要设置按钮边框颜色，标签字体颜色与大小等
def set_popover_style():
    st.markdown(
        """
        <style>
            /* 修改popover容器边框为橙色 */
            div[data-testid="stPopover"] {
                border: 1px solid #FF8C00 !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            }
            
            /* 修改所有 popover 按钮的字体大小 */
            div[data-testid="stPopover"] button {
                font-size: 1.2rem !important;
                font-weight: bold;
                color: orange; /* 这里也可以改颜色 */
            }    
        </style>
    """, unsafe_allow_html=True)

# #-------------------------------------------------------------------------
# 3. st.dataframe数据rows斑马纹显示
# # 注意：dataframe数据行数大，页面渲染有延迟卡顿现象，性能明显降低

def set_alternating_colors(df):
    # 创建一个空列表用于存储样式
    styles = []
    for i, _ in df.iterrows():
        # 偶数行（索引0, 2...）设为浅灰，奇数行（索引1, 3...）设为白色（或反之）
        # 注意：Streamlit 默认背景通常是白色或透明，这里我们显式设置
        color = '#f0f2f6' if i % 2 == 0 else '#ffffff' 
        # 这里的样式是针对整行的
        styles.extend([[f'background-color: {color}'] * len(df.columns)])
    return pd.DataFrame(styles, index=df.index, columns=df.columns)

    # def alternating_colors(df):
    #     """
    #     接收整个 DataFrame，返回一个形状相同的样式 DataFrame
    #     """
    #     # 创建一个与原 DataFrame 形状相同的空 DataFrame，用于存放样式
    #     # 默认样式可以是空字符串 '' 或者默认背景色
    #     styles = pd.DataFrame('', index=df.index, columns=df.columns)
        
    #     # 定义偶数行的样式 (例如：浅灰色)
    #     # 注意：这里利用 index % 2 == 0 来筛选行
    #     styles.loc[df.index % 2 == 0, :] = 'background-color: #f2f2f2'
        
    #     #奇数行保持默认（白色），或者你可以显式设置另一种颜色
    #     styles.loc[df.index % 2 == 1, :] = 'background-color: #ffffff'
        
    #     return styles

# #-------------------------------------------------------------------------
# 4. st.markdown文本前面添加logo。注意：logo为项目文件夹存储的本地文件
def markdown_with_logo(value, image_path):
    
    # 将本地图片转换为base64编码
    def get_image_base64(image_path):
        # 判断image路径是否存在，不存在使用font字体图标
        if Path(image_path).exists():
            used_image = image_path
        else:
            used_image = 'static/images/default.jpeg'
        try:
            with open(used_image, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return None

    image_base64 = get_image_base64(image_path)
   
    st.markdown(
        f'''
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="data:image/jpeg;base64,{image_base64}" 
                style="width: 20px; height: 20px; object-fit: cover; display: inline-block;">
            <span style="color: #1c82e1; font-size: 16px; font-weight: bold; display: inline-block;">{value}</span>
        </div>
        ''',
        unsafe_allow_html=True
    )

# #-------------------------------------------------------------------------
# 5. 去掉页面顶部空白，右上角deploy按钮等
def set_pagetop_style():
    st.markdown(
        """
        <style>
            /* 1. 只隐藏右上角的Deploy按钮，保留左上角的菜单按钮 */
            .stDeployButton {display: none;}
            
            /* 2. 隐藏页脚和右上角的菜单图标（如果不需要） */
            footer {visibility: hidden;}
            
            /* 3. 移除内容区域的顶部内边距，但给header留出空间 */
            .block-container {
                padding-top: 0rem;  /* 保留一点空间给header，避免内容太靠上 */
                padding-bottom: 2rem;
            }
            
            /* 4. 可选：让header半透明或缩小高度，但保留按钮 */
            header {
                background-color: rgba(255, 255, 255, 0.5);
                backdrop-filter: blur(0px);
                height: 1rem;  /* 减小header高度 */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# #-------------------------------------------------------------------------
# 6. st.navigation导航块样式设置
def set_navigation_style():
    st.markdown(
        """
        <style>
            /* ========== 导航区域样式合并 ========== */
            
            /* 
            * 1. 导航容器整体样式 
            * 合并了间距调整和视觉美化属性
            */
            [data-testid="stSidebarNav"] {
                /* --- 间距调整 --- */
                margin-top: -25px !important;       /* 从 set_navigation_style 中移入 */
                margin-bottom: 5px !important;      /* 从 set_navigation_style 中移入，覆盖了原来的 1.5rem */
                padding-top: 0 !important;          /* 从 set_navigation_style 中移入 */
                padding-bottom: 1rem !important;    /* 保留原美化样式，但被下面的 0 覆盖 */

                /* --- 视觉美化 --- */
                position: relative;                 /* 保留原美化样式，用于伪元素定位 */
                border-radius: 8px;                 /* 保留原美化样式 */
                background: linear-gradient(180deg, rgba(102, 126, 234, 0.02) 0%, rgba(102, 126, 234, 0) 100%); /* 保留原美化样式 */
            }
            
            /* 修正：由于上面设置了 padding-bottom: 0 !important，这里需要重新应用，
            或者在上面直接设置为你想要的值。根据 set_navigation_style 的意图，
            可能你希望底部间距也很小。这里我们遵从 set_navigation_style 的意图，
            将 padding-bottom 设为 0。
            */
            [data-testid="stSidebarNav"] {
                padding-bottom: 0 !important;
            }

            /* 2. 辅助分割线 - 增加层次感 */
            [data-testid="stSidebarNav"]::before {
                content: '';
                position: absolute;
                bottom: 6px;
                left: 15%;
                right: 15%;
                height: 1px;
                background: linear-gradient(90deg, transparent, #667eea, #764ba2, #667eea, transparent);
                border-radius: 1px;
            }
            
            /* 3. 导航项悬停效果优化 */
            [data-testid="stSidebarNav"] li a {
                transition: all 0.2s ease;
                border-radius: 6px;
                margin: 2px 0;
            }
            
            [data-testid="stSidebarNav"] li a:hover {
                background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
                transform: translateX(2px);
            }
            
            /* 4. 当前激活页面高亮 */
            [data-testid="stSidebarNav"] li a[aria-current="page"] {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
                border-left: 3px solid #667eea;
                font-weight: 500;
            }
            
            /* 5. 让下方组件与导航区域有明确的视觉分隔 */
            .stSidebar .stMarkdown:first-of-type {
                margin-top: 0.5rem;
            }

            /* 6. 调整侧边栏主要内容容器的内边距 */
            [data-testid="stSidebarUserContent"] {
                padding-top: 0 !important;
            }
            
            /* 7. 如果导航下面还有额外的间距 */
            .st-emotion-cache-1w1fy6i {
                margin-bottom: 5px !important;
            }
            
            /* 8. 调整侧边栏整体布局 */
            section[data-testid="stSidebar"] > div:first-child {
                padding-top: 1rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# #-------------------------------------------------------------------------
# 7. 隐藏st.dataframe下载按钮，或是隐藏整个工具栏
def hide_dataframe_toolbar():
    # 注入 CSS 代码来隐藏工具栏
    st.markdown(
        """
        <style>
            [data-testid="stElementToolbar"] {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # # 隐藏第三个按钮（下载按钮）, 检查组件布局定位下载按钮位于第几个
    # st.markdown(
    #     """
    #     <style>
    #         /* 隐藏数据框工具栏里的第三个按钮（下载按钮） */
    #         [data-testid="stElementToolbarButton"]:nth-child(3) {
    #             display: none !important;
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )

if __name__ == '__main__':
    pass
