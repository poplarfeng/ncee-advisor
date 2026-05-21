# -*- coding: utf-8 -*-

# #导入python标准模块
import numpy as np
from typing import cast, Any

# #导入第三方模块
import streamlit as st
import pandas as pd
import plotly.express as px

# #导入自定义模块
from dataset import load_data_schools, load_china_provinces_geojson
from settings import (
    PROVINCE_NAME_MAPPING, 
    set_divider_style, 
    set_popover_style,
    set_pagetop_style,
    set_navigation_style
) 
from settings import set_alternating_colors
from school_distribute_map import school_distribute_map


# #设置全局页面样式
st.set_page_config(
    page_title="高考志愿填报智能推荐系统",
    # page_icon="🎓",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# #初始化会话状态变量data_loaded， 在数据装载之前初始化为False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# #初始化 Tab 状态
if 'school_main_tab' not in st.session_state:
    st.session_state.school_main_tab = ':clipboard: 院校列表'

# ###############################################################################
# 设置CSS样式
# ###############################################################################
set_divider_style()
set_popover_style()
set_pagetop_style()
set_navigation_style()

# #初始化加载数据, 该页面应用需要加载 高校综合信息数据、中国省份地图地理数据
def init_data():
    # ----------------------------------------------------------------------------
    # 加载数据，加载失败streamlit应用停止运行
    # ----------------------------------------------------------------------------
    # 创建一个占位容器，用于在加载时显示消息，加载完成后清空或替换
    if not st.session_state.data_loaded:
        placeholder = st.empty()
        try:
            with placeholder.status('🚀 广东省高考数据加载中，请稍后...'):
                st.write('加载高校信息中... (1/2)')
                raw_schools = load_data_schools()
                st.write('加载地图数据中... (2/2)')
                china_provinces_geo = load_china_provinces_geojson()
            placeholder.empty()
        except:
            placeholder.error(f"⚠️数据文件加载失败!")
            st.stop()

        st.session_state.data_loaded = True
    else:
        raw_schools = load_data_schools()
        china_provinces_geo = load_china_provinces_geojson()

    return raw_schools, china_provinces_geo

# #数据清洗，包括数据一致性处理，格式转换以及缺失值处理等
def clean_data(raw_schools):

    score_cols = ['2022分数线', '2023分数线', '2024分数线', '2025分数线']

    # 复制数据，后续处理不影响原始数据
    clean_schools = raw_schools.copy()
    clean_schools['软科排名'] = clean_schools['软科排名'].replace(0, np.nan)
    # 将分数列为0的数据转换成缺失值 np.nan
    clean_schools[score_cols] = clean_schools[score_cols].replace(0, np.nan)
    # for col in score_cols:
    #     df_schools_selected[col] = df_schools_selected[col].replace(0, np.nan)
    # ---------------------------------------------------------------------------------------------
    # 下面的语句在pandas 3.0+版本会有告警提示，推荐使用当前的语法
    # df_schools_seclected.loc[:, score_cols] = df_schools_selected.loc[:, score_cols].replace(0, np.nan)

    # 将省份datafame中省份数据与geojson文件中的省份名称保持一致
    clean_schools['省份'] = clean_schools['省份'].map(PROVINCE_NAME_MAPPING)


    return clean_schools


if __name__ == '__main__':

    # #初始化数据，返回数据格式类型为dataframe、geojson
    raw_schools, china_provinces_geo = init_data()

    # #清洗数据，返回清洗后的dataframe类型数据，后续数据操作都在清洗后的数据基础上进行处理
    clean_schools = clean_data(raw_schools)

    # #############################################################################
    # 定义sidebar侧边栏
    # 1.定义sidebar侧边栏筛选控件数据=================================================
    provinces = sorted(raw_schools['省份'].dropna().unique())
    province_options = ['不限'] + list(provinces)
    f985 = raw_schools['F985'].dropna().unique()
    f985_options = ['不限'] + list(f985)
    f211 = raw_schools['F211'].dropna().unique()
    f211_options = ['不限'] + list(f211)
    dual_class = raw_schools['双一流'].dropna().unique()
    dual_class_options = ['不限'] + list(dual_class)
    school_nature = raw_schools['办学体制'].dropna().unique()
    school_nature_options = ['不限'] + list(school_nature)
    school_level = raw_schools['办学层次'].dropna().unique()
    schoool_level_options = ['不限'] + list(school_level)

    # 2.定义sidebar侧边栏筛选控件========================================================
    with st.sidebar:
        with st.container(gap='xxsmall'):
            # st.header("🔍 查询条件")
            st.subheader(':material/search: 查询条件')
            st.divider()

            # 增加“选科类型”筛选选型
            subject_choice = st.selectbox('选科类型', options=['物理类', '历史类'], index=0)
            province_choice = st.selectbox('学校省份', options=province_options, index=0)
            f985_choice = st.selectbox('是否985', options=f985_options, index=0)
            f211_choice = st.selectbox('是否211', options=f211_options, index=0)
            dual_class_choice = st.selectbox('是否双一流', options=dual_class_options, index=0)
            school_nature_choice = st.selectbox('办学体制', options=school_nature_options, index=0)
            school_level_choice = st.selectbox('办学层次', options=schoool_level_options, index=0)

    # ################################################################################
    # 根据侧边栏组件选项筛选数据
    # 1.根据选科类型筛选
    clean_schools = clean_schools[clean_schools['选科类型'] == subject_choice]

    # 2.根据省份筛选
    if province_choice != '不限':
        clean_schools = clean_schools[clean_schools['省份'] == province_choice]

    # 3.根据是否985筛选
    if f985_choice != '不限':
        clean_schools = clean_schools[clean_schools['F985'] == f985_choice]

    # 4.根据是否211筛选
    if f211_choice != '不限':
        clean_schools = clean_schools[clean_schools['F211'] == f211_choice]

    # 5.根据办学体制筛选
    if school_nature_choice != '不限':
        clean_schools = clean_schools[clean_schools['办学体制'] == school_nature_choice]

    # 6.根据办学层次筛选
    if school_level_choice != '不限':
        clean_schools = clean_schools[clean_schools['办学层次'] == school_level_choice]

    # ##################################################################################
    # 定义主页面 
    # （✅已筛选出<span style='color:red'>{len(clean_schools)}</span>条数据）
    st.markdown(
        f"##### :material/shadow: 全国高校综合信息数据查询结果 ",
        unsafe_allow_html=True
    )

    st.divider(width='stretch')

    # #定义主页面Tabs =======================================================================
    school_tabs = st.tabs(
        [':clipboard: 院校列表', ':blue[:material/location_on:] 院校地理分布'],
        default=st.session_state.school_main_tab,
        key="school_main_tab"  # <<< 显式 Key 是解决第一次跳转的关键)
    )
    # 1.全国高校综合信息Tab ------------------------------------------------------------------
    with school_tabs[0]:
        st.session_state.school_main_tab = ':clipboard: 院校列表'

        # # 应用斑马纹样式并显示 注：应用样式后页面明显延迟卡顿，用户体验下降
        # # 使用 df.style.apply() 传入函数，axis=None 表示应用于整个表格
        # styled_clean_schools = clean_schools.style.apply(alternating_colors, axis=None)

        # 隐藏不显示的列
        columns_to_hide = ['选科类型', 'ID']
        columns_to_show = [col for col in clean_schools.columns if col not in columns_to_hide]

        event_schools_table = st.dataframe(
            clean_schools, 
            width='stretch',
            height=400,
            hide_index=True,
            column_order=columns_to_show,     # 通过column_order实现隐藏不显示的列
            on_select='rerun'
        )

        event_schools_table = cast(Any, event_schools_table)

        #event_df为选择'高校列表'dataframe的事件响应数据
        if event_schools_table and event_schools_table.selection.rows:

            rows_selected = event_schools_table.selection.rows
            # --------------------------------------------------------------------
            # 从展示的dataframe中筛选出所选学校的信息
            schools_selected = clean_schools.iloc[rows_selected]

            # ---------------------------------------------------------------------
            # 将所筛选出的dataframe从'宽数据'转换为'长数据'格式
            # 不变列-学校名称， 转换列-2022分数线，2023分数线，2024分数线，2025分数线
            score_cols = ['2022分数线', '2023分数线', '2024分数线', '2025分数线']
            schools_selected_melted = schools_selected.melt(
                id_vars=['学校名称'], 
                value_vars=score_cols,
                var_name='年份',
                value_name='分数线'
            )
            # 修改dataframe'年份'列 如 2022分数线-->2022，并显性化更改在数字类型
            schools_selected_melted['年份'] = schools_selected_melted['年份'].str.replace('分数线', '')
            schools_selected_melted['年份'] = schools_selected_melted['年份'].astype(int)

            # --------------------------------------------------------------------------------------------------
            # schools_selected_melted['学校名称', '年份', '分数线'], 下面合并进软科排名，None替换缺失值
            school_rank = clean_schools[['学校名称', '软科排名']]
            school_rank['软科排名'] = school_rank['软科排名'].fillna(None)
            schools_selected_melted = schools_selected_melted.merge(school_rank, on='学校名称', how='left')
            schools_selected_melted['软科排名'] = schools_selected_melted['软科排名'].astype(object).fillna('--')

            # ---------------------------------------------------------------------------------------------------
            # 通过px.line()绘制分数线趋势图
            score_fig = px.line(
                schools_selected_melted, 
                x='年份', 
                y='分数线', 
                color='学校名称', 
                hover_name='学校名称',
                # hover_data=['年份', '分数线'],
                custom_data=['年份', '软科排名', '分数线'],
                markers=True,
                title='近四年分数线趋势',
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            
            score_fig.update_traces(
                line_shape='spline',
                # hovertemplate='<b>%{hovertext}</b><br>年份：%{x}<br>分数线：%{y}<extra></extra>',
                hovertemplate='<b>%{hovertext}</b><br>' + '软科排名: %{customdata[1]}<br>' + '分数线: %{customdata[2]}<extra></extra>',
            )

            score_fig.update_layout(
                hovermode='x unified',
                xaxis=dict(
                    # 1. 设置刻度模式为“以整数对齐”
                    tickmode='linear', 
                    # 2. 设置起始位置 (取数据中的最小年份)
                    tick0=schools_selected_melted['年份'].min(), 
                    # 3. 设置步长为 1 (即 2022,2023, 2024, 2025...)
                    dtick=1,
                    showgrid=False,
                ),
                yaxis=dict(
                    showgrid=True,
                    griddash='dot',
    
                )
            )

            # #-----------------------------------------------------------------------------
            # 定义popover组件，装载分数线趋势图
            popover_label1= f':chart_with_upwards_trend: 点击查看所选高校近四年录取分数线趋势详情 (✅已选择 :red[{len(schools_selected)}] 所高校)......'
            with st.popover(label=popover_label1, width='stretch'):
                st.plotly_chart(score_fig, width='stretch')
        else:
            st.info(':information_source: :blue[未选择学校无趋势图显示，想要查看历年录取分数趋势变化，请在"高校列表"栏进行勾选......]')

    # 2.全国高校分布地图Tab ------------------------------------------------------------------
    with school_tabs[1]:

        event_provinces_map = school_distribute_map(clean_schools, china_provinces_geo)

        # 分隔地图与下方展示的数据
        # st.divider(width='stretch')

        # event_map为点选地图区域的事件响应数据
        if event_provinces_map and event_provinces_map.selection.points:

            # 【关键】显式声明：现在依然在 Tab 1 (高校分布)
            # 这样即使页面重跑，st.tabs 也会因为 default=current_tab 而保持在地图页
            st.session_state.school_main_tab = ':blue[:material/location_on:] 院校地理分布' 

            # 获取选择的省份信息，如：广东省
            province_selected = event_provinces_map.selection.points[0].get('location')

            # ------------------------------------------------------------------------------------------
            # 根据获取的省份信息，从clean_schools dataframe筛选出对应省份的高校综合信息，显示在地图下方
            # 为了不影响前面显示的数据，筛选出的数据作为一个独立的副本
            schools_province_selected = clean_schools[clean_schools['省份'] == province_selected]
            
            # st.markdown(
            #      f"###### 【<span style='color:red'>{event_map_province}</span>】高校综合信息数据查询 （✅总共<span style='color:red'>{len(event_map_selected )}</span>所高校）",
            #     unsafe_allow_html=True
            # )
            # # 应用样式并显示
            # # 使用 df.style.apply() 传入函数，axis=None 表示应用于整个表格 
            schools_province_selected_resetindex = schools_province_selected.reset_index(drop=True)

            # # 格式化方法1 --------------------------------------------------------------------------------------
            # schools_province_selected_resetindex['保研率'] = schools_province_selected_resetindex['保研率'].map(lambda x: f'{x:.2f}')
            # styled_schools_selected = schools_province_selected_resetindex.style.apply(alternating_colors, axis=None)

            # # 格式化方法2 --------------------------------------------------------------------------------------
            # 定义需要格式化的列和格式
            format_dict = {
                '保研率': '{:.2f}',  # 2位小数
                # '其他数值列': '{:.2f}',  # 如果有其他列需要格式化
                # '百分比列': '{:.1%}',  # 如果需要显示为百分比
            }
            styled_schools_selected = (schools_province_selected_resetindex
                .style
                .apply(set_alternating_colors, axis=None)
                .format(format_dict)
            )

            popover_label2= f'【:red[{province_selected}]】高校综合信息(✅符合条件 :red[{len(schools_province_selected )}] 所),点击查看详情......'

            with st.popover(label=popover_label2, width='stretch'):

                # 显示所点选省份的高校综合信息（注：当前地图装载的数据[df_schools_selected dataframe]是主页面筛选条件过滤后的数据）
                st.markdown(
                   f'###### :material/layers: {province_selected}', unsafe_allow_html=True
                )
                st.dataframe(
                    styled_schools_selected, 
                    width='stretch',
                    # height=400,
                    hide_index=True,
                    column_order=columns_to_show
                )
        else:
            st.info(':information_source: :blue[需要查看某个省份高校综合信息，请在地图上点选相应区域]......')

