# -*- coding: utf-8 -*-

# 导入标准模块
from pathlib import Path
import base64

# 导入第三方模块
import streamlit as st
import pandas as pd

# 导入自定义模块
from settings import set_divider_style, set_pagetop_style, set_navigation_style, set_alternating_colors
from settings import PROVINCE_NAME_MAPPING, PROVINCE_TO_REGION, RECOMMEND_RANK_PARAMS
from dataset import load_data_schools, load_data_specials, load_data_specialgroups, load_china_provinces_geojson
from school_distribute_map import school_distribute_map


# #初始化会话状态变量data_loaded， 在数据装载之前初始化为False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# #初始化会话转态变量recommend_trigger，点击"开始智能推荐"按钮触发会话状态变化
if 'recommend_trigger' not in st.session_state:
    st.session_state.recommend_trigger = False

# #初始化会话转态变量recommend_school_tab, 定义默认展示哪个tab
if 'recommend_school_tab' not in st.session_state:
    st.session_state.recommend_school_tab = ':material/book_2: 稳妥院校'

# 页面配置
st.set_page_config(
    page_title="高考志愿填报智能推荐系统",
    # page_icon="🎓",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded"
)

set_divider_style()
set_pagetop_style()
set_navigation_style()

# ###############################################################################
# #初始化加载数据, 该页面应用需要加载 高校所有专业录取数据
def init_data():

    # 加载数据，加载失败streamlit应用停止运行
    # 创建一个占位容器，用于在加载时显示消息，加载完成后清空或替换
    if not st.session_state.data_loaded:
        placeholder = st.empty()

        try:
            with placeholder.status('🚀 广东省高考数据加载中，请稍后...'):
                st.write('加载专业录取信息中... (1/4)')
                raw_specials = load_data_specials()
                st.write('加载高校综合信息中... (2/4)')
                raw_schools = load_data_schools()
                st.write('加载专业组录取信息中... (3/4)')
                raw_specialgroups = load_data_specialgroups()
                st.write('加载中国地图各省份地理数据中... (4/4)')
                geo_china = load_china_provinces_geojson()
            placeholder.empty()
        except:
            placeholder.error(f"⚠️数据文件加载失败!")
            st.stop()

        st.session_state.data_loaded = True
    else:
        raw_specials = load_data_specials()
        raw_schools = load_data_schools()
        raw_specialgroups = load_data_specialgroups()
        geo_china = load_china_provinces_geojson()

    return raw_specials, raw_schools, raw_specialgroups, geo_china
    
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

# 定制推荐院校与专业页面显示样式
def render_school_card_with_expander(df: pd.DataFrame, default_expanded=False):
    """使用自定义 HTML/CSS/JS 实现完全可控的折叠卡片，使用 st.iframe 渲染
    
    Args:
        df: 包含学校数据的DataFrame
        default_expanded: 默认是否展开，False为默认收起
    """
    if df.empty:
        st.info(':information_source: :blue[没有符合条件的推荐院校...]')
        return None, None
    
    school_names = df['学校名称'].dropna().unique()
    
    # 生成完整的 HTML
    cards_html = ""
    for school_name in school_names:
        data_by_school = df[df['学校名称'] == school_name]
        school_id = data_by_school.iloc[0]['ID']
        
        # 获取学校图标
        image_path = f'static/images/{school_id}.jpg'
        image_base64 = get_image_base64(image_path)
        
        # 构建专业的 HTML
        specialties_html = ""
        special_names = data_by_school['专业名称'].dropna().unique()
        
        for special_name in special_names:
            data_by_special = data_by_school[data_by_school['专业名称'] == special_name]
            years = sorted(data_by_special['招生年份'].dropna().unique())
            
            scores_html = ""
            for year in years:
                data_year = data_by_special[data_by_special['招生年份'] == year]
                score = data_year['录取线'].iloc[0]
                rank_val = data_year['名次排位'].iloc[0]
                scores_html += f'<span class="year-score">{year}: {score}/{rank_val}</span>'
            
            specialties_html += f"""
            <div class="specialty-row">
                <div class="specialty-name">{special_name}</div>
                <div class="year-scores">{scores_html}</div>
            </div>
            """
        
        # 根据 default_expanded 参数决定初始状态
        if default_expanded:
            content_class = "school-content"
            toggle_icon = "..."
        else:
            content_class = "school-content collapsed"
            toggle_icon = ">"
        
        cards_html += f"""
        <div class="school-card">
            <div class="school-header" onclick="toggleCard(this)">
                <div class="school-header-left">
                    <img src="data:image/jpeg;base64,{image_base64}" class="school-icon">
                    <span class="school-name">{school_name}</span>
                </div>
                <span class="toggle-icon">{toggle_icon}</span>
            </div>
            <div class="{content_class}">
                {specialties_html}
            </div>
        </div>
        """
    
    # 完整的 HTML 页面
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                padding: 1px;
                line-height: 1.0;
            }}
            
            .school-card {{
                margin-bottom: 12px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            
            .school-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 12px;
                background: #fafbfc;
                cursor: pointer;
                user-select: none;
                transition: background 0.2s ease;
            }}
            
            .school-header:hover {{
                background: #f0f2f5;
            }}
            
            .school-header-left {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .school-icon {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                object-fit: cover;
                display: block;
            }}
            
            .school-name {{
                font-weight: 600;
                font-size: 15px;
                color: #1a3c4a;
                letter-spacing: -0.3px;
            }}
            
            .toggle-icon {{
                transition: transform 0.3s ease;
                font-size: 14px;
                color: #666;
            }}
            
            .school-content {{
                padding: 16px;
                transition: all 0.3s ease-in-out;
                max-height: 2000px;
                overflow: hidden;
                opacity: 1;
                visibility: visible;
            }}
            
            .school-content.collapsed {{
                max-height: 0;
                padding: 0 12px;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease-in-out;
            }}
            
            .specialty-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.15s ease;
            }}
            
            .specialty-row:hover {{
                background: #fafcfd;
            }}
            
            .specialty-row:last-child {{
                border-bottom: none;
            }}
            
            .specialty-name {{
                font-weight: 500;
                font-size: 14px;
                min-width: 150px;
                color: #2c5a6e;
            }}
            
            .year-scores {{
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                align-items: center;
            }}
            
            .year-score {{
                background: #f0f4f8;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 13px;
                color: #3a6b82;
                transition: background 0.2s ease;
                white-space: nowrap;
            }}
            
            .year-score:hover {{
                background: #e6edf4;
                color: #1a5a74;
            }}
            
            @media (max-width: 640px) {{
                .specialty-row {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }}
                .specialty-name {{
                    font-size: 14px;
                }}
                .year-score {{
                    white-space: normal;
                    font-size: 12px;
                }}
            }}
        </style>
        <script>
            function toggleCard(header) {{
                const content = header.nextElementSibling;
                const icon = header.querySelector('.toggle-icon');
                content.classList.toggle('collapsed');
                icon.textContent = content.classList.contains('collapsed') ? '>' : '...';
            }}
        </script>
    </head>
    <body>
        {cards_html if cards_html else '<div class="empty-placeholder">暂无推荐院校数据</div>'}
    </body>
    </html>
    """
    
    # 直接使用 st.iframe 传入 HTML 字符串，无需临时文件
    # height 使用 "content" 让 iframe 自动适应内容高度[citation:1]
    # st.iframe(full_html, height='content')
    return full_html, school_names

# 生成推荐院校与专业数据，包括页面显示html代码
@st.cache_data
def caculate_recommend_schools(
    clean_specials, subject_choice, zslx_choice, batch_choice, region_preference, year_reference, score, rank, score_rank_selection
):
    # 筛选选科类型数据
    clean_specials = clean_specials[clean_specials['选科类型'] == subject_choice]
    # 筛选招生类型数据
    if zslx_choice != '不限':
        clean_specials = clean_specials[clean_specials['招生类型'] == zslx_choice]
    # 筛选招生批次数据
    if '不限' not in batch_choice:
        clean_specials = clean_specials[clean_specials['招生批次'].isin(batch_choice)]
    # 筛选地域偏好数据
    if region_preference != '不限':
        clean_specials = clean_specials[clean_specials['省份'].isin(PROVINCE_TO_REGION[region_preference])]
    if year_reference != '不限':
        clean_specials = clean_specials[clean_specials['招生年份'] == year_reference]

    if score_rank_selection == ':chart_with_upwards_trend: 按名次':
        # 初始化智能推荐数据，按照三个类别计算：保底院校、稳妥院校、冲刺院校
        safe_rank_low = int(rank*(1 + RECOMMEND_RANK_PARAMS['rank']['safe'][0]))
        safe_rank_high = int(rank*(1 + RECOMMEND_RANK_PARAMS['rank']['safe'][1]))
        schools_safe = clean_specials[(clean_specials['名次排位'] >= safe_rank_low) & (clean_specials['名次排位'] < safe_rank_high)]

        target_rank_low = int(rank*(1 + RECOMMEND_RANK_PARAMS['rank']['target'][0]))
        target_rank_high= int(rank*(1 + RECOMMEND_RANK_PARAMS['rank']['target'][1]))
        schools_target = clean_specials[(clean_specials['名次排位'] >= target_rank_low) & (clean_specials['名次排位'] <= target_rank_high)]

        challenge_rank_low = int(rank*(1 + RECOMMEND_RANK_PARAMS['rank']['challenge'][0]))
        challenge_rank_high = int(rank*(1 + RECOMMEND_RANK_PARAMS['rank']['challenge'][1]))
        schools_challenge = clean_specials[(clean_specials['名次排位'] > challenge_rank_low) & (clean_specials['名次排位'] <= challenge_rank_high)]

    elif score_rank_selection == ':page_with_curl: 按分数':
        # 初始化智能推荐数据，按照三个类别计算：保底院校、稳妥院校、冲刺院校
        safe_score_low = int(score + RECOMMEND_RANK_PARAMS['score']['safe'][0])
        safe_score_high= int(score + RECOMMEND_RANK_PARAMS['score']['safe'][1])
        schools_safe = clean_specials[(clean_specials['录取线'] >= safe_score_low) & (clean_specials['录取线'] < safe_score_high)]

        target_score_low = int(score + RECOMMEND_RANK_PARAMS['score']['target'][0])
        target_score_high = int(score + RECOMMEND_RANK_PARAMS['score']['target'][1])
        schools_target = clean_specials[(clean_specials['录取线'] >= target_score_low) & (clean_specials['录取线'] <= target_score_high)]

        challenge_score_low = int(score + RECOMMEND_RANK_PARAMS['score']['challenge'][0])
        challenge_score_high = int(score + RECOMMEND_RANK_PARAMS['score']['challenge'][1])
        schools_challenge = clean_specials[(clean_specials['录取线'] > challenge_score_low) & (clean_specials['录取线'] <= challenge_score_high)]
    else:
        pass

    # 保底院校、稳妥院校与冲刺院校推荐页面结构生成
    html_content_safe, school_names_safe = render_school_card_with_expander(schools_safe, default_expanded=False)
    html_content_target, school_names_target = render_school_card_with_expander(schools_target, default_expanded=False)
    html_content_challenge, school_names_challenge = render_school_card_with_expander(schools_challenge, default_expanded=False)

    return (
    html_content_safe, school_names_safe,
    html_content_target, school_names_target,
    html_content_challenge, school_names_challenge,
    schools_safe, schools_target, schools_challenge
)

# 推荐院校各省份分布
@st.fragment
def get_recommend_schools_distribution(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame):
    """
    1. 根据推荐档位选择，通过地图展示各省份推荐院校高校数量
    2. 根据在地图上点选省份区域，通过st.dataframe展示所选省份推荐院校与专业详细信息
    3. df1,df2,df3 对应计算出来的推荐院校数据schools_safe,schools_target,schools_challenge
    """
    with st.container(gap='xxsmall'):
        recommend_map_col1, _= st.columns([2, 9], vertical_alignment='center')
        with recommend_map_col1:   
            recommend_level = st.selectbox('推荐档位', options=['保底院校', '稳妥院校', '冲刺院校'], index=1, label_visibility='collapsed')
        
        df_dict = {'保底院校': df1, '稳妥院校': df2, '冲刺院校': df3}
        df = df_dict.get(recommend_level, df2)

        # 对应的dataframe为空，函数直接返回，停止执行后面的代码
        if df.empty:
            st.info(':information_source: :blue[没有符合条件的推荐院校...]')
            return

        # 准备地图展示数据    
        df_group_by_school = df.groupby('学校名称').agg({
            '省份': 'first'
        })
    
    # 生成高校在各省份地图分布, 通过变量接收地图点击事件
    event_school_distribution = school_distribute_map(df_group_by_school, geo_china)
    
    # 根据地图点击，获取点击省份，生成该省份数据，然后进行st.dataframe展示
    if event_school_distribution and event_school_distribution.selection.points:

        province_select = event_school_distribution.selection.points[0].get('location')
        schools_province_select = df[df['省份'] == province_select]
        # 在st.dataframe展示时隐藏'选科类型'与'ID'两列
        columns_hide = ['选科类型', 'ID']
        columns_show = [col for col in schools_province_select if col not in columns_hide]
        # 计算选择省份数据院校数量与专业数量
        school_nums = len(schools_province_select['学校名称'].dropna().unique())
        special_nums = len(schools_province_select)
        # 重置索引，用于在st.dataframe展示时应用斑马纹效果
        schools_provice_select_resetindex = schools_province_select.reset_index(drop=True)
        styled_schools_province_select = (
            schools_provice_select_resetindex
            .style
            .apply(set_alternating_colors, axis=None)
        )

        popover_label_province = f'【:red[{province_select}]】推荐院校与专业详细信息(✅院校 【:red[{school_nums}]】所, 专业【:red[{special_nums}]】个), 点击查看详情......'
        with st.popover(label=popover_label_province, width='stretch'):

            # 显示所点选省份推荐院校与专业信息（注：当前地图装载的数据是对应的推荐档位院校数据
            st.markdown(
                f'###### :material/layers: {province_select}', unsafe_allow_html=True
            )
            st.dataframe(
                styled_schools_province_select, 
                width='stretch',
                # height=400,
                hide_index=True,
                column_order=columns_show
            )
    else:
        st.info(':information_source: :blue[需要查看某个省份推荐院校与专业详细信息，请在地图上面点选相应区域...]')

# ###################################################################################
# 初始化数据
raw_specials, raw_schools, raw_specialgroups, geo_china = init_data()
# # 将专业组2025年的数据，合并到专业数据（注：专业数据线去掉2025年的数据）
# temp_specials = raw_specials[raw_specials['招生年份'] != 2025]
# temp_specialgroups = raw_specialgroups[raw_specialgroups['招生年份'] == 2025]
# common_cols = temp_specials.columns.intersection(temp_specialgroups.columns)
# clean_specials = pd.concat([temp_specials[common_cols], temp_specialgroups[common_cols]], ignore_index=True)
clean_specials = raw_specials.copy()
clean_specials['省份'] = clean_specials['省份'].map(PROVINCE_NAME_MAPPING)

# ####################################################################################
# sidebar侧边栏设置
# ####################################################################################
with st.sidebar:
    with st.container(gap='xxsmall'):
        st.subheader(':material/cognition: 志愿填报助手')
        # st.markdown("""
        #     <div style="font-size: 1.1rem; opacity: 1.0; text-align: left; font-weight: bold; margin-bottom: 1rem;">
        #         志愿填报助手
        #     </div>
        #     """, unsafe_allow_html=True)
        # st.markdown("""
        #         <div style="font-size: 0.8rem; opacity: 0.7; text-align: center;">
        #             智能分析，精准推荐
        #         </div>
        #     """, unsafe_allow_html=True)
        # st.space()
        st.divider()
        st.markdown("#### :material/data_check: 考生信息")
        st.divider()
        st.space()
        score_rank_selection = st.segmented_control(
                label='选择类别',
                options=[':page_with_curl: 按分数', ':chart_with_upwards_trend: 按名次'],
                selection_mode='single',
                required=True,
                default=':chart_with_upwards_trend: 按名次',
                label_visibility='collapsed'
            )
        score = st.number_input("高考总分", 0, 750, 560)
        rank = st.number_input("全省位次", 1000, 400000, 65000)
        subject_choice = st.selectbox('选科类型', options=['物理类', '历史类'], index=0)
        zslx_types = sorted(raw_specials['招生类型'].dropna().unique())
        zslx_options = ['不限'] + list(zslx_types)
        zslx_default_index = zslx_options.index('普通类')
        zslx_choice = st.selectbox('招生类型', options=zslx_options, index=zslx_default_index)
        # 增加招生批次筛选项
        batch_types = sorted(raw_specials['招生批次'].dropna().unique())
        batch_options = ['不限'] + list(batch_types)
        batch_choice = st.multiselect('招生批次', options=batch_options, default=['本科批', '专科批'])
        st.markdown("#### :material/data_check: 偏好设置")
        st.divider()
        region_preference = st.selectbox('地域偏好', options=['不限'] + list(PROVINCE_TO_REGION.keys()), index=0)
        year_reference = st.selectbox('参考年份', options=['不限'] + [2021, 2022, 2023, 2024, 2025], index=0)
        st.space()
        recommend_btn = st.button('开始智能推荐', type='primary', width='stretch')
        # 定义清空数据按钮
        recommend_clear_btn = st.button(':material/delete: 清空数据', width='stretch')

# ####################################################################################
# 按钮处理逻辑（放在前面），可以规避点击"清空数据"按钮时，推荐院校代码还会执行的错误逻辑
# ####################################################################################
# 点击"开始智能推荐"按钮，变更会话状态变量recommend_trigger值
if recommend_btn:
    st.session_state.recommend_trigger = True
    st.rerun()

# 点击"清空数据"按钮，变更会话状态变量recommend_trigger值
if recommend_clear_btn:
    st.session_state.recommend_trigger = False
    st.session_state.recommend_school_tab = ':material/book_2: 稳妥院校'  # 重置tab
    st.rerun()

# ####################################################################################
# 主页面设置
######################################################################################
# 智能推荐默认页面CSS样式，显示还没有获取考生信息之前的页面展示
st.markdown("""
    <style>
        /* 主页面欢迎区域 */
        .welcome-container {
            text-align: center;
            padding: 1rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin-bottom: 1rem;
            color: white;
        }
        
        .welcome-title {
            font-size: 1.6rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .welcome-subtitle {
            font-size: 1rem;
            opacity: 0.95;
            margin-bottom: 0.5rem;
        }
        
        /* 功能介绍卡片 */
        .feature-card {
            background: white;
            padding: 1.2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        .feature-icon {
            font-size: 2.0rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.0rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }
        
        .feature-desc {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

# 初始化一个容器，用于装载主页面“欢迎”部分下面的内容, 用于切换功能介绍和推荐结果
header_area = st.empty()
result_area = st.empty()
status_area = st.empty()       

# 在没有点击智能推荐按钮前，显示初始化页面
if not st.session_state.recommend_trigger:
    # 主页面内容 
    # 欢迎区域
    with header_area.container():
        st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">
                    欢迎使用志愿填报智能推荐系统
                </div>
                <div class="welcome-subtitle">
                    基于大数据分析，为您精准匹配理想院校
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    ⭐ 请在左侧侧边栏填写考生信息，点击「开始智能推荐」获取专属志愿方案
                </div>
            </div>
            """, unsafe_allow_html=True)

    with result_area.container():
        # 功能介绍
        st.markdown("#### ✨ 功能介绍")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">智能分析</div>
                    <div class="feature-desc">基于历年院校专业录取数据，智能预测录取概率</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">精准匹配</div>
                    <div class="feature-desc">结合分数、名次排位、偏好，推荐合适院校专业</div>
                </div>
                """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <div class="feature-title">多维推荐</div>
                    <div class="feature-desc">冲刺、稳妥、保底三级推荐，科学填报高考志愿</div>
                </div>
                """, unsafe_allow_html=True)

        st.space()
        st.divider()

        # 温馨提示
        st.markdown("""
            <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                <strong>💡 温馨提示：</strong><br>
                1. 推荐结果仅供参考，建议结合官方招生简章综合考量<br>
                2. 录取概率基于往年数据预测，实际录取受当年报考情况影响<br>
                3. 建议按照「冲刺-稳妥-保底」的梯度原则填报志愿<br>
                4. 如有疑问，可查看其他页面的详细数据作为参考
            </div>
            """, unsafe_allow_html=True)
    
# 触发智能推荐，执行业务处理逻辑    
else:
    # 重新生成主页面“欢迎”部分下面的内容
    with status_area.status(':material/genetics: 志愿填报推荐院校与专业智能计算中，请稍后...'):
        results = caculate_recommend_schools(
            clean_specials, subject_choice, zslx_choice, batch_choice, region_preference, year_reference, score, rank, score_rank_selection
        )
        # 接收返回数据
        html_content_safe, school_names_safe = results[:2]
        html_content_target, school_names_target = results[2:4]
        html_content_challenge, school_names_challenge = results[4:6]
        schools_safe, schools_target, schools_challenge = results[6:9]
    status_area.empty()

    with result_area.container():
        # 定义推荐院校标题栏
        st.markdown(
            f"##### :material/shadow: 高考志愿填报院校与专业推荐",
            unsafe_allow_html=True
        )

        # 推荐院校与专业主体展示区
        recommend_school_tabs = st.tabs(
            [':material/book: 保底院校', ':material/book_2: 稳妥院校', ':material/book_3: 冲刺院校', ':blue[:material/location_on:] 推荐院校地理分布', ':clipboard: 院校与专业录取列表'],
            default=st.session_state.recommend_school_tab,
            key='recommend_school_tab'
        )

        #展示保底推荐院校与专业页面
        with recommend_school_tabs[0]:
            # html_content_safe, school_names_safe = show_recommend_schools(schools_safe)
            if school_names_safe:
                st.markdown(
                        f"###### ✅保底填报院校推荐:orange[【{len(school_names_safe)}】]所",
                        unsafe_allow_html=True
                    )
                # 使用 st.iframe 渲染，height 根据行数动态调整会更完美，这里设为固定紧凑高度
                st.iframe(html_content_safe, height='content')
            else:
                st.info(':information_source: :blue[没有符合条件的推荐院校...]')

        # 展示稳妥推荐院校与专业页面
        with recommend_school_tabs[1]:
            # html_content_target, school_names_target = show_recommend_schools(schools_target)
            if school_names_target:
                st.markdown(
                        f"###### ✅稳妥填报院校推荐:orange[【{len(school_names_target)}】]所",
                        unsafe_allow_html=True
                    )
                # 使用 st.iframe 渲染，height 根据行数动态调整会更完美，这里设为固定紧凑高度
                st.iframe(html_content_target, height='content')
            else:
                st.info(':information_source: :blue[没有符合条件的推荐院校...]')

        # 展示冲刺推荐院校与专业页面
        with recommend_school_tabs[2]:
            # html_content_challenge, school_names_challenge = show_recommend_schools(schools_challenge)
            if school_names_challenge:
                st.markdown(
                        f"###### ✅冲刺填报院校推荐:orange[【{len(school_names_challenge)}】]所",
                        unsafe_allow_html=True
                    )
                # 使用 st.iframe 渲染，height 根据行数动态调整会更完美，这里设为固定紧凑高度
                st.iframe(html_content_challenge, height='content')
            else:
                st.info(':information_source: :blue[没有符合条件的推荐院校...')

        # 展示推荐院校各省份分布地图，可以根据推荐档位进行过滤
        with recommend_school_tabs[3]:
            get_recommend_schools_distribution(schools_safe, schools_target, schools_challenge)
        
        # 展示所有院校与专业清单，通过条件可以筛选保底、稳妥与冲刺推荐院校    
        with recommend_school_tabs[4]:
            @st.fragment
            def recommend_school_table():
                column_order = ['招生年份', '学校名称', '专业名称', '专业详情', '录取线', '名次排位', '招生人数', '录取人数', '一级分类', '二级分类', '三级分类', '办学体制', '办学层次', '招生类型', '招生批次']
                with st.container(gap='xxsmall'):
                    recommend_table_col1, recommend_table_col2, _, recommend_table_col3, recommend_table_col4 = st.columns([2,3,7,2,3], vertical_alignment='center')
                    with recommend_table_col1:
                        st.write('推荐档位')
                    with recommend_table_col2:   
                        schools_detail_table = st.selectbox('推荐档位', options=['不限'] + ['保底推荐', '稳妥推荐', '冲刺推荐'], index=0, label_visibility='collapsed')
                    with recommend_table_col3:
                        st.write('招生批次')
                    with recommend_table_col4:
                        if schools_detail_table == '保底推荐':
                            batch_names = sorted(schools_safe['招生批次'].dropna().unique())
                        elif schools_detail_table == '稳妥推荐':
                            batch_names = sorted(schools_target['招生批次'].dropna().unique())
                        elif schools_detail_table == '冲刺推荐':
                            batch_names = sorted(schools_challenge['招生批次'].dropna().unique())
                        else:
                            batch_names = sorted(clean_specials['招生批次'].dropna().unique())
                        batch_options = ['不限'] + list(batch_names)
                        batch_choice = st.selectbox('招生批次', options=batch_options, index=0, label_visibility='collapsed')
                    if schools_detail_table == '保底推荐':
                        if not schools_safe.empty:
                            schools_safe_table = schools_safe.copy()
                            if batch_choice != '不限':
                                schools_safe_table = schools_safe_table[schools_safe_table['招生批次'] == batch_choice]
                            st.dataframe(
                                schools_safe_table, 
                                hide_index=True, 
                                column_order=column_order
                            )
                        else:
                            st.info(':information_source: :blue[没有符合条件的推荐院校...]')

                    elif schools_detail_table == '稳妥推荐':
                        if not schools_target.empty:
                            schools_target_table = schools_target.copy()
                            if batch_choice != '不限':
                                schools_target_table = schools_target_table[schools_target_table['招生批次'] == batch_choice]
                            st.dataframe(
                                schools_target_table, 
                                hide_index=True, 
                                column_order=column_order
                            )
                        else:
                            st.info(':information_source: :blue[没有符合条件的推荐院校...]')

                    elif schools_detail_table == '冲刺推荐':
                        if not schools_challenge.empty:
                            schools_challenge_table = schools_challenge.copy()
                            if batch_choice != '不限':
                                schools_challenge_table = schools_challenge_table[schools_challenge_table['招生批次'] == batch_choice]
                            st.dataframe(
                                schools_challenge_table, 
                                hide_index=True, 
                                column_order=column_order
                            )
                        else:
                            st.info(':information_source: :blue[没有符合条件的推荐院校...]')

                    else:
                        schools_all_table = clean_specials.copy()
                        if batch_choice != '不限':
                            schools_all_table = schools_all_table[schools_all_table['招生批次'] == batch_choice]
                        st.dataframe(
                            schools_all_table, 
                            hide_index=True, 
                            height=450,
                            column_order=column_order
                        )

            # 执行上面定义的函数，定义成函数的目的是用@st.fragmeng装饰，在函数内组件状态变化时，只重新运行该函数代码        
            recommend_school_table()


