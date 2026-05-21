# -*- coding: utf-8 -*-

# 导入标准模块
import base64
from pathlib import Path

# 导入第三方模块
import streamlit as st
import pandas as pd


# #设置全局页面样式
st.set_page_config(
    page_title="广东高考录取数据查询系统",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def build_special_schools_show(df: pd.DataFrame):
    
    df = df
    # 计算统计指标
    school_count = len(df['学校名称'].dropna().unique())
    total_students = f'{df["招生人数"].sum():.0f}'
    max_students = df["招生人数"].max() 

    # 构建表格行
    table_rows = ""
    for _, row in df.iterrows():
        school_id = row['ID']
        school_name = row["学校名称"]
        score = row['录取线']
        students = row["招生人数"]
        students_formatted = f'{students:.0f}'
        duration = row["学制年数"]
        tuition = row["学费"]
        tuition_formatted = f'¥{tuition:,.0f}'
        admission_type = row['招生类型']
        
        # 进度条宽度计算
        progress_width = (students / max_students) * 100

         # 将本地图片转换为base64编码
        @st.cache_data
        def get_image_base64(image_path):
            image_path = image_path
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
            
        image_path = f'static/images/{school_id}.jpg'
        image_base64 = get_image_base64(image_path)
        
        table_rows += f"""
        <tr>
            <td>
                <div class="school-cell">
                    <img src="data:image/jpeg;base64,{image_base64}" alt="logo" class="school-icon">
                    <span class="school-name">{school_name}</span>
                </div>
            </td>
            <td><span class="score-cell">{score}</span></td>
            <td>
                <div class="student-cell">
                    <div class="student-number">{students_formatted}</div>
                    <div class="progress-bg">
                        <div class="progress-bar" style="width: {progress_width}%"></div>
                    </div>
                </div>
            </td>
            <td><span class="duration-badge">{duration}</span></td>
            <td><span class="admission-type">{admission_type}</span></td>
        </tr>
        """
    
    # 使用 st.iframe 替代旧的 html 组件
    # srcdoc 允许直接在 iframe 中写入 HTML 代码
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{
                --primary: #4f46e5;
                --text-main: #1e293b;
                --text-sub: #64748b;
                --border: #f1f5f9;
            }}
            * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
            body {{ padding: 10px; color: var(--text-main); }}
            
            /* 紧凑统计卡片 */
            .stats-row {{ display: flex; gap: 10px; margin-bottom: 15px; }}
            .stat-item {{
                display: flex; align-items: center; padding: 6px 12px;
                background: #fff; border: 1px solid #e2e8f0;
                border-radius: 6px; font-size: 0.8rem;
                box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            }}
            .stat-val {{ font-weight: 700; margin-left: 8px; }}
            
            /* 表格基础 */
            table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
            th {{
                text-align: left; padding: 8px 12px;
                color: var(--text-sub); font-weight: 600;
                border-bottom: 2px solid #e2e8f0;
                font-size: 0.75rem; text-transform: uppercase;
            }}
            td {{
                padding: 10px 12px; /* 3. 优化：缩小行高 */
                border-bottom: 1px solid var(--border);
                vertical-align: middle;
            }}
            /* 2. 优化：取消斑马纹，统一白色背景 */
            tr {{ background-color: #fff; }}
            tr:hover {{ background-color: #f8fafc; }}
            
            /* 元素样式微调 */
            .school-cell {{ display: flex; align-items: center; gap: 5px; }}
            .school-icon {{
                width: 15px; height: 15px; background: #f1f5f9;
                border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 1rem;
            }}
            .student-cell {{ display: flex; flex-direction: column; gap: 2px; }}
            .score-cell {{ color: #475569; font-size: 0.75rem; font-weight: 600; color: var(--primary);}}
            .student-number {{ font-weight: 600; color: var(--primary); }}
            .progress-bg {{ width: 60px; height: 3px; background: #e2e8f0; border-radius: 2px; }}
            .progress-bar {{ height: 100%; background: var(--primary); border-radius: 2px; }}
            .duration-badge {{
                background: #f1f5f9; color: #475569;
                padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;
            }}
            .tuition-amount {{ color: #059669; font-weight: 600; font-family: monospace; }}
            .admission-type {{ color: #475569; font-size: 0.75rem; }}
        </style>
    </head>
    <body>
        <div class="stats-row">
            <div class="stat-item">🏫 学校 <span class="stat-val">{school_count}</span></div>
            <div class="stat-item">👥 总人数 <span class="stat-val">{total_students}</span></div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>学校名称</th>
                    <th>分数线</th>
                    <th>招生人数</th>
                    <th>学制年数</th>
                    <th>招生类型</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # 使用 st.iframe 渲染，height 根据行数动态调整会更完美，这里设为固定紧凑高度
    st.iframe(html_content, height=450)


if __name__ == '__main__':
    pass