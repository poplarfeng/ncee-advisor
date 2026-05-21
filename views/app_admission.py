# -*- coding: utf-8 -*-

# #导入标准模块
from typing import cast, Any

# #导入第三方模块
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# #导入自定义模块
from dataset import load_data_specials, load_data_schools, load_data_specialgroups, load_china_provinces_geojson
from settings import (
    set_alternating_colors,
    set_divider_style, 
    set_popover_style, 
    set_pagetop_style,
    markdown_with_logo,
    set_navigation_style,
    PROVINCE_NAME_MAPPING
)
from school_overview import load_css, load_layout
from special_schools_query import build_special_schools_show
from school_distribute_map import school_distribute_map
from specials_by_school import set_specials_bar


# 设置全局页面样式
st.set_page_config(
    page_title="高考志愿填报智能推荐系统",
    # page_icon="🎓",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态变量data_loaded， 在数据装载之前初始化为False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'special_main_tab' not in st.session_state:
    st.session_state.special_main_tab = ':red[:material/home:] 符合院校'

if 'school_special_tab' not in st.session_state:
    st.session_state.school_special_tab = ':material/home: 学校概览'

if 'special_analysis_tab' not in st.session_state:
    st.session_state.special_analysis_tab = ':material/home: 学校概览'


# ###############################################################################
# 设置CSS样式
# ###############################################################################
set_divider_style()
set_popover_style()
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
                st.write('加载地图数据中... (4/4)')
                china_provinces_geo = load_china_provinces_geojson()
            placeholder.empty()
        except:
            placeholder.error(f"⚠️数据文件加载失败!")
            st.stop()

        st.session_state.data_loaded = True
    else:
        raw_specials = load_data_specials()
        raw_schools = load_data_schools()
        raw_specialgroups = load_data_specialgroups()
        china_provinces_geo = load_china_provinces_geojson()

    return raw_specials, raw_schools, raw_specialgroups, china_provinces_geo


if __name__ == '__main__':

    raw_specials, raw_schools, raw_specialgroups, china_provinces_geo = init_data()
    # #############################################################################
    # # 将专业组2025年的数据，合并到专业数据（注：专业数据线去掉2025年的数据）
    # temp_specials = raw_specials[raw_specials['招生年份'] != 2025]
    # temp_specialgroups = raw_specialgroups[raw_specialgroups['招生年份'] == 2025]
    # common_cols = temp_specials.columns.intersection(temp_specialgroups.columns)
    # clean_specials = pd.concat([temp_specials[common_cols], temp_specialgroups[common_cols]], ignore_index=True)

    clean_specials = raw_specials.copy()
    clean_schools = raw_schools.copy()
    # 将省份datafame中省份数据与geojson文件中的省份名称保持一致
    clean_schools['省份'] = clean_schools['省份'].map(PROVINCE_NAME_MAPPING)
    clean_specialgroups = raw_specialgroups.copy()

    # ###############################################################################
    # 定义sidebar侧边栏
    # 1.定义sidebar侧边栏筛选控件数据=================================================
    # 筛选组件数据，包含单选与多选options
    years = sorted(raw_specials['招生年份'].dropna().unique())
    year_options = ['不限'] + [int(year) for year in years if pd.notna(year)]
    provinces = sorted(raw_specials['省份'].dropna().unique())
    province_options = ['不限'] + list(provinces)
    zslx_types = sorted(raw_specials['招生类型'].dropna().unique())
    zslx_options = ['不限'] + list(zslx_types)
    batch_names = sorted(raw_specials['招生批次'].dropna().unique())
    batch_options = ['不限'] + list(batch_names)

    # 2.计算dataframe分数，名次排位数据集================================================
    min_score = raw_specials['录取线'].min()
    max_score = raw_specials['录取线'].max()
    min_rank = raw_specials['名次排位'].min()
    max_rank = raw_specials['名次排位'].max()

    # 3.定义筛选组件，使用sidebar用于在页面左边展示=========================================
    # radio -> 用于按照分数/名次排位进行筛选，二选七一
    # slider -> 按照范围，作用于'分数'与'名次排位'列
    # selectbox -> 选择招生年份，默认不限，单选
    # multiseclect -> 选择大学所在省份，默认不限，可以多选
    # selectbox -> 选择招生类型，默认不限，单选
    # selectbox -> 选择招生批次，默认不限，单选
    with st.sidebar:
        with st.container(gap='xxsmall'):

            # st.header("🔍 查询条件")
            st.subheader(':material/search: 查询条件')
            st.divider()

            st.markdown("#### :material/data_check: 查询模式")
            score_or_rank = st.radio(   
                label='选择类型',
                options=['按分数', '按名次'],
                index=0,
                horizontal=True,
                # key='score_or_rank',
                label_visibility="collapsed"  # 👈 关键参数：完全隐藏标签且不留空白
            )

            st.markdown("#### :material/data_check: 范围设定")

            if score_or_rank == '按分数':    
                score_range = st.slider(
                    '录取分数范围选择', 
                    min_value=min_score,
                    max_value=max_score,
                    value=(min_score, max_score),
                    label_visibility='collapsed'
                )
                rank_range = None
            else:
                rank_range = st.slider(
                    '名次排位范围选择', 
                    min_value=min_rank,
                    max_value=max_rank,
                    value=(min_rank, max_rank),
                    label_visibility='collapsed'
                )
                score_range = None

            st.markdown("#### :material/data_check: 详细属性")
            st.divider()

            # 增加“选科类型”筛选项
            subject_choice = st.selectbox('选科类型', options=['物理类', '历史类'], index=0)
            year_choice = st.multiselect('招生年份', options=year_options, default=['不限'], help='可多选,只要包含【不限】即为全选')
            province_choice = st.multiselect('学校省份', options=province_options, default=['不限'], help='可多选')
            zslx_choice = st.selectbox('招生类型', options=zslx_options, index=0)
            batch_choice = st.selectbox('招生批次', options=batch_options, index=0)
            
    # ################################################################################################
    # 根据过滤条件值进行数据计算
    # 增加根据“选科类型”筛选数据 =======================================================================
    clean_schools = clean_schools[clean_schools['选科类型'] == subject_choice]
    clean_specials = clean_specials[clean_specials['选科类型'] == subject_choice]
    clean_specialgroups = clean_specialgroups[clean_specialgroups['选科类型'] == subject_choice]

    # 1.按分数或名次排位筛选
    if score_or_rank == '按分数' and score_range:
        low, high = score_range
        clean_specials = clean_specials[
            (clean_specials['录取线'] >= low) &
            (clean_specials['录取线'] <= high)
        ]
    elif score_or_rank == '按名次' and rank_range:
        low, high = rank_range
        clean_specials = clean_specials[
            (clean_specials['名次排位'] >= low) &
            (clean_specials['名次排位'] <= high)
        ]

    # 2.根据招生年份筛选
    if '不限' not in year_choice:
        clean_specials = clean_specials[clean_specials['招生年份'].isin(year_choice)]

    # 3.根据学校省份筛选
    if '不限' not in province_choice:
        clean_specials = clean_specials[clean_specials['省份'].isin(province_choice)]

    # 4.根据招生类型筛选
    if zslx_choice != '不限':
        clean_specials = clean_specials[clean_specials['招生类型'] == zslx_choice]

    # 5.根据招生批次筛选
    if batch_choice != '不限':
        clean_specials = clean_specials[clean_specials['招生批次'] == batch_choice]

    # ##########################################################################################################
    # 定义主窗口数据展示
    #  （✅已筛选出<span style='color:red'>{len(clean_specials)}</span>条数据）
    st.markdown(
        f"##### :material/shadow: 广东省高考全国高校专业录取数据查询结果",
        unsafe_allow_html=True
    )
    # st.info(f'总共筛选出{len(df_selected)}条数据！')

    st.divider(width='stretch')

    # #定义主页面Tabs =======================================================================
    special_tabs = st.tabs(
        [':red[:material/home:] 符合院校', ':blue[:material/location_on:] 院校地理分布', ':clipboard: 符合专业列表', ':bar_chart: 专业分数分布'],
        default=st.session_state.special_main_tab,
        key="special_main_tab"  # <<< 显式 Key 是解决第一次跳转的关键)
    )

    # 符合查询分数/名次排位范围院校清单，展示：学校名称、所有专业的最低录取线、学校概览信息
    with special_tabs[0]:
        st.session_state.special_main_tab = ':red[:material/home:] 符合院校'
        schools_agg = clean_specials.groupby('学校名称').agg({
            '录取线': 'min',                    # 最低录取线
            '名次排位': 'max',                  # 最佳名次
            '招生人数': 'sum',
            # 基本信息使用 first() - 因为每行都一样
            'F985': 'first',
            'F211': 'first',
            '双一流': 'first',
            '办学体制': 'first',
            '办学层次': 'first',
            '省份': 'first',
            '城市': 'first',
            '办学层次': 'first',
        }).reset_index()

        event_schools_agg = st.dataframe(
            schools_agg, 
            width='stretch',
            height=400,
            hide_index=True,
            on_select='rerun',
            selection_mode='single-row'
        )

        event_schools_agg = cast(Any, event_schools_agg)

        #event_df为选择dataframe的事件响应数据
        if event_schools_agg and event_schools_agg.selection.rows:
            # 获取选择的索引行，返回格式为列表，如[1]
            schools_agg_row = event_schools_agg.selection.rows
            # --------------------------------------------------------------
            # 从展示的dataframe中筛选出所选学校的信息,通过iloc[[]]筛选，返回dataframe
            schools_agg_selected = schools_agg.iloc[schools_agg_row[0]]
            school_name_agg = schools_agg_selected['学校名称']
            school_id_agg = clean_schools[clean_schools['学校名称'] == school_name_agg].squeeze()['ID']

            popover_label1= f':material/home: :red[【{school_name_agg}】]学校概览、所有专业录取详细信息，请点击查看......'
            with st.popover(label=popover_label1, width='stretch'):
                image_path = f'static/images/{school_id_agg}.jpg'
                markdown_with_logo(school_name_agg, image_path)

                school_special_tabs = st.tabs(
                    [':material/home: 学校概览', ':clipboard: 专业列表', ':bar_chart: 专业分析'],
                    default=st.session_state.school_special_tab,
                    key="school_special_tab" 
                )
                # 展示学校基本概况，服用school_overview模板
                with school_special_tabs[0]:
                    school_show_agg = clean_schools[clean_schools['学校名称'] == school_name_agg]
                    school_show_agg[['F985', 'F211', '双一流']] = school_show_agg[['F985', 'F211', '双一流']].replace({'是': True, '否': False})
                    load_css()
                    load_layout(school_show_agg.squeeze())
                
                # 展示选择院校符合条件的专业录取清单
                with school_special_tabs[1]:
                    schools_agg_selected_specials = clean_specials[clean_specials['学校名称'] == school_name_agg]
                    columns_special_show = ['招生年份', '专业名称', '录取线', '名次排位', '招生人数', '专业详情', '一级分类', '二级分类', '三级分类', '招生类型', '招生批次']
                    st.dataframe(
                        schools_agg_selected_specials,
                        column_order=columns_special_show,
                        hide_index=True
                    )

                # 通过柱状图展示选择院校符合条件所有专业间对比
                with school_special_tabs[2]:
                    specials_by_school_1 = clean_specials[clean_specials['学校名称'] == school_name_agg]
                    colunms_required_1 = ['招生年份', '专业名称', '二级分类', '三级分类', '录取线', '名次排位', '招生类型', '招生批次', '专业详情']
                    specials_by_school_1 = specials_by_school_1[colunms_required_1]
                    specials_by_school_1 = specials_by_school_1.rename(columns={'二级分类': '专业类别', '三级分类': '专业子类', '录取线': '分数线'})
                    set_specials_bar(specials_by_school_1, clean_specialgroups)
                                
        else:
            st.info(':information_source: :blue[想要查看院校所有专业录取详细信息，请在"符合院校"栏进行勾选......]')

    # 符合院校在各省的分布，通过中国地图展示
    with special_tabs[1]:
        # st.session_state.special_main_tab = ':blue[:world_map:] 院校分布'
        # 将省份datafame中省份数据与geojson文件中的省份名称保持一致
        schools_agg['省份'] = schools_agg['省份'].map(PROVINCE_NAME_MAPPING)
        event_provinces_map = school_distribute_map(schools_agg, china_provinces_geo)

        # event_map为点选地图区域的事件响应数据
        if event_provinces_map and event_provinces_map.selection.points:
    
            st.session_state.school_main_tab = ':blue[:material/location_on:] 院校地理分布'
            # 获取选择的省份信息，如：广东省
            province_selected = event_provinces_map.selection.points[0].get('location')
            # ------------------------------------------------------------------------------------------
            # 根据获取的省份信息，从clean_schools dataframe筛选出对应省份的高校综合信息，显示在地图下方
            # 为了不影响前面显示的数据，筛选出的数据作为一个独立的副本
            schools_province_selected = schools_agg[schools_agg['省份'] == province_selected]
            
            # st.markdown(
            #      f"###### 【<span style='color:red'>{event_map_province}</span>】高校综合信息数据查询 （✅总共<span style='color:red'>{len(event_map_selected )}</span>所高校）",
            #     unsafe_allow_html=True
            # )
            # # 应用样式并显示
            # # 使用 df.style.apply() 传入函数，axis=None 表示应用于整个表格 
            schools_province_selected_resetindex = schools_province_selected.reset_index(drop=True)
            styled_schools_provinces_selected = (schools_province_selected_resetindex
                .style
                .apply(set_alternating_colors, axis=None)
            )

            popover_label2= f'【:red[{province_selected}]】符合院校信息(✅符合条件 :red[{len(schools_province_selected )}] 所),点击查看详情......'

            with st.popover(label=popover_label2, width='stretch'):

                # 显示所点选省份的高校综合信息（注：当前地图装载的数据[df_schools_selected dataframe]是主页面筛选条件过滤后的数据）
                st.markdown(
                f'###### :material/layers: {province_selected}', unsafe_allow_html=True
                )
                school_province_selected = st.dataframe(
                    styled_schools_provinces_selected, 
                    width='stretch',
                    # height=400,
                    hide_index=True,
                    # on_select='rerun',
                    # selection_mode='single-row'
                )
        else:
            st.info(':information_source: :blue[需要查看某个省份符合条件院校信息，请在地图上点选相应区域]......')

    # 符合查询分数/名次排位范围的所有专业清单，展示dataframe所有数据
    with special_tabs[2]:

        # st.session_state.special_main_tab = ':clipboard: 符合专业列表'
        if len(clean_specials) == 0:
            st.info(':information_source: 没有符合筛选条件的数据，请在边侧栏选择有效的查询条件...', width='stretch')
        else:
            # 隐藏不显示的列
            columns_to_hide = ['选科类型', 'ID']
            columns_to_show = [col for col in clean_specials.columns if col not in columns_to_hide]
            st.dataframe(
                clean_specials, 
                width='stretch',
                # height=500,
                column_order=columns_to_show,     # 通过column_order实现隐藏不显示的列
                hide_index=True
            )

    # 符合查询分数/名次排位范围的所有专业录取全局分布    
    with special_tabs[3]:

        # st.session_state.special_main_tab = ':bar_chart: 专业分数分布'

        # #根据过滤后的数据，计算"招生年份"清单，用于图标排序
        if len(clean_specials) == 0:
            st.info(':information_source: 没有符合筛选条件的数据，请在边侧栏选择有效的查询条件...', width='stretch')
        else:
            category_orders = clean_specials['招生年份'].dropna().unique()
            category_orders = sorted([int(year) for year in category_orders])

            chart_title = f'所选高校专业录取分数线分布({min(category_orders)}-{max(category_orders)})' \
            if len(category_orders) > 1 \
            else f'所选高校专业录取分数线分布({category_orders[0]})'

            with st.container(gap='xxsmall'):

                chart_type_selection = st.segmented_control(
                    label='选择图形类别',
                    options=[':material/shadow: 叠加图', ':material/menu: 分面图'],
                    selection_mode='single',
                    required=True,
                    default=':material/shadow: 叠加图',
                    label_visibility='collapsed'
                )

                # #-------------------------------------------------------------------------------
                # #引用前面计算过的分数线最小值与最大值，用于绘制直方图x轴数值范围, min_score/max_score
                # 设置直方图nbins值
                min_score_dynamic = clean_specials['录取线'].min()
                max_score_dynamic = clean_specials['录取线'].max()
                nbins = int(max_score_dynamic - min_score_dynamic)

                if chart_type_selection == ':material/shadow: 叠加图':
                    # #--------------------------------------------------------------------------------
                    # #所有高校专业录取分数线分布，数据不随着过滤条件而变化，始终呈现全部数据的分布
                    # #全部数据源为clean_specials, 2021-2025五年数据overlay模式绘制在一张分布图上
                    # #--------------------------------------------------------------------------------
                    fig_specials_overlay = px.histogram(
                        clean_specials,
                        x='录取线',
                        color='招生年份',
                        nbins=nbins,
                        title=chart_title,
                        labels={'录取线': '录取分数线', 'count': '专业数量'},
                        opacity=0.5,   # 关键：设置透明度，防止完全遮挡
                        text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Set1,
                        category_orders={'招生年份': category_orders}
                    )

                    fig_specials_overlay.update_traces(
                        # hovertemplate 是自定义显示的模板
                        # <extra></extra> 用于隐藏默认显示在第二行的显示数据，让界面更干净
                        hovertemplate=(
                            "<b>招生年份: %{data.name}</b><br>"
                            "录取分数线：%{x}<br>"
                            "专业数量：%{y}<br>"
                            "<extra></extra>"
                        )
                    )

                    fig_specials_overlay.update_layout(
                        barmode='overlay',
                        showlegend=True,
                        xaxis={
                            'title': '录取分数线',
                            'range': [min_score, max_score]
                        },
                        yaxis_title='专业数量'
                    )

                    # # #更新Y轴专用函数，在分面图中可以更新所有子图Y轴
                    # fig_specials_all.update_yaxes(title_text="专业数量")

                    st.plotly_chart(fig_specials_overlay, width='stretch')
                    
                elif chart_type_selection == ':material/menu: 分面图':
                    # #计算分面图数量
                    facets_n = len(category_orders)
                    # #--------------------------------------------------------------------------------
                    # #所有高校专业录取分数线分布，数据不随着过滤条件而变化，始终呈现全部数据的分布
                    # #全部数据源为clean_specials, 2021-2025五年数据facet模式,不同年份绘制在不同子图上
                    # #--------------------------------------------------------------------------------
                    fig_specials_facet = px.histogram(
                        clean_specials,
                        x='录取线',
                        facet_col='招生年份',
                        facet_col_wrap=1,
                        nbins=nbins,
                        # color_discrete_sequence=px.colors.carto.Blugrn_r,
                        title=chart_title,
                        labels={'录取线': '录取分数线', 'count': '专业数量'},
                        opacity=0.6,   # 关键：设置透明度，防止完全遮挡
                        # text_auto=True,
                        category_orders={'招生年份': category_orders}
                    )
                    
                    # #-----------------------------------------------------------------------------------
                    # #核心修改：处理分面标题
                    # #遍历图表中所有的注释（annotations）
                    # #-------------------------------------------------------------------------------
                    for annotation in fig_specials_facet['layout']['annotations']:
                        annotation = cast(Any, annotation)
                        # 检查注释文本是否包含 "招生年份="
                        if "招生年份=" in annotation['text']:
                            # 将文本替换为等号后面的内容（即年份）
                            annotation['text'] = annotation['text'].split('=')[1] + '年'
                            # 使用 .update() 方法,可以更安全合并现有的字体设置
                            annotation.update(
                                font=dict(
                                    weight='bold',  # 关键：设置为粗体
                                    size=15,        # 可选：稍微加大字号让标题更醒目
                                    color="#333333" # 可选：加深颜色
                                )
                            )

                    fig_specials_facet.update_traces(
                        # hovertemplate 是自定义显示的模板
                        # <extra></extra> 用于隐藏默认显示在第二行的显示数据，让界面更干净
                        hovertemplate=(
                            "录取分数线：%{x}<br>"
                            "专业数量：%{y}<br>"
                            "<extra></extra>"
                        )
                    )
                    fig_specials_facet.update_layout(
                        showlegend=False,
                        height=400*facets_n,
                        xaxis=dict(
                            showticklabels=True,  # 强制显示所有子图的 X 轴刻度
                            range=[min_score, max_score]
                        )
                    )
                    # 设置Y轴，matches=None表示分面图Y轴不统一，每个Y轴自适配高度
                    fig_specials_facet.update_yaxes(title_text="专业数量", matches=None)

                    # # 获取所有 y 轴对象
                    # yaxes = [axis for axis in fig_specials_facet.layout if axis.startswith('yaxis')]

                    # # 遍历每个 y 轴，进行个性化设置
                    # for yaxis in yaxes:
                    #     fig_specials_facet.layout[yaxis].update(
                    #         # matches=None,  # 解除Y轴同步，允许每个子图有自己的Y轴范围
                    #         showticklabels=True,  # 确保显示刻度标签
                    #         title_text="专业数量"  # 为每个子图的Y轴都设置标题
                    #     )

                    # 同样，确保每个子图的X轴也显示刻度
                    xaxes = [axis for axis in fig_specials_facet.layout if axis.startswith('xaxis')]
                    for xaxis in xaxes:
                        fig_specials_facet.layout[xaxis].update(
                            showticklabels=True  # 确保每个子图的X轴都显示刻度标签
                        )

                    st.plotly_chart(fig_specials_facet, width='stretch')