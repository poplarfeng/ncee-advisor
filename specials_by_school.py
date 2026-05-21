# -*- coding: utf-8 -*-

# 导入标准模块
import random

# 导入第三方模块
import streamlit as st
import plotly.express as px

# 导入自定义模块
from special_schools_query import build_special_schools_show


# 根据学校名称筛选出符合条件的所有专业，绘制柱状图，展示各专业各年份的录取线
def set_specials_bar(specials_df, specialgroups_df):
    # #赋值一份副本，在tabs[1]可以根据专业进行过滤，不影响tab[0]的表格展示
    specials_by_school = specials_df.copy()

    title_analysis_col1, title_analysis_col2, title_analysis_col3 = st.columns([5, 7, 2], vertical_alignment='center')
    with title_analysis_col1:
        # #----------------------------------------------------------------------------------------
        # #专业对比选项，设置成可按分数，或是按名次排位进行分析
        special_analysis_type = st.segmented_control(
            label='选择图形类别',
            options=['按分数', '按名次'],
            selection_mode='single',
            default='按分数',
            required=True,
            label_visibility='collapsed',
        )
    with title_analysis_col2:
        special_select_col1, special_select_col2 = st.columns([1, 4], vertical_alignment='center')
        with special_select_col1:
            st.markdown("选择专业:")
        with special_select_col2:      
            specials = sorted(specials_by_school['专业名称'].dropna().unique())
            special_options =  ['不限'] + list(specials)
            special_choice = st.selectbox(
                '选择专业',
                options=special_options,
                index=0,
                label_visibility='collapsed'
            )

    # #根据所选专业计算开设院校，通过st.popover容器展示
    with title_analysis_col3:
        with st.popover('开设院校', width='stretch'):
            colunms_required_all = [
                'ID',
                '招生年份',
                '学校名称',
                '录取线',
                '专业名称',
                '招生人数',
                '学制年数',
                '学费',
                '招生批次',
                '招生类型',
                '二级分类',
                '三级分类'
            ]
            specialgroups_all = specialgroups_df[colunms_required_all]
            specialgroups_all = specialgroups_all[specialgroups_all['招生年份'] == 2025]
            specialgroups_all = specialgroups_all.rename(columns={'二级分类': '专业类别', '三级分类': '专业子类'})
            specialgroups_show = specialgroups_all.copy()

            # # 根据所选择的专业名称，筛选出需要在页面展示的数据
            if special_choice != '不限':

                # 通过container撑大显示宽度----------------------------------------------------------------------
                with st.container(width=800):
                    specialgroups_show = specialgroups_show[specialgroups_show['专业名称'] == special_choice]
                    specialgroups_show['学制年数'] = specialgroups_show['学制年数'].replace({'3': '三年', '4': '四年', '5': '五年', '8': '八年'})
                    
                    # specialgroups_show.sort_values(by='招生人数', ascending=False, inplace=True)
                    # 页面显示数据按照录取线进行降序排列
                    specialgroups_show.sort_values(by='录取线', ascending=False, inplace=True)
                    if len(specialgroups_show) != 0:
                        special_type = specialgroups_show.iloc[0]['专业类别']
                        special_subtype = specialgroups_show.iloc[0]['专业子类']
                        # 招生批次去重后的种类
                        show_batch = list(specialgroups_show['招生批次'].dropna().unique())
                        show_options = ['不限'] + show_batch
                        
                        # 招生批次选择selectbox默认值
                        if '本科批' in show_options:
                            batch_default_value = '本科批'
                        elif '专科批' in show_options:
                            batch_default_value = '专科批'
                        else:
                            batch_default_value = '非本科专科批'
                        
                        default_index = show_options.index(batch_default_value) if batch_default_value in show_options else 0

                        show_col1, show_col2= st.columns([7, 3], vertical_alignment='bottom')
                        with show_col1:
                            st.markdown(f'<h6 style="color: #1c82e1;">{special_choice}</h6>', unsafe_allow_html=True)
                            st.caption(f'{special_type} - {special_subtype}')
                        with show_col2:
                            batch_selected = st.selectbox(
                                label='选择招生批次',
                                options=show_options,
                                index=default_index,
                                label_visibility='collapsed',
                            )
                        if batch_selected != '不限':
                            specialgroups_show = specialgroups_show[specialgroups_show['招生批次'] == batch_selected]    
                        # st.dataframe(specialgroups_show, width='stretch', hide_index=True)
                        build_special_schools_show(specialgroups_show)
                    else:
                        st.info(f':information_source: :blue[截至2025年，院校已取消 {special_choice} 专业设置......]')
                    

    
    # #-----------------------------------------------------------------------------------------------------------
    # # 根据选择的专业进行数据过滤，用于图表展示，默认为所有专业
    if special_choice != '不限':
        specials_by_school = specials_by_school[specials_by_school['专业名称'] == special_choice]
    
    # # ----------------------------------------------------------------------------------------------------------
    # # 按分数展示逻辑进行数据计算与图表展示
    if special_analysis_type == '按分数':
        # #------------------------------------------------------------------------------------------------------
        # 进行去重
        # subset=['专业名称', '招生年份'] 指定根据这两列来判断是否重复
        # keep='first' 表示保留排序后的第一条（也就是分数最高的那一条）
        specials_by_school = specials_by_school.sort_values('分数线', ascending=False)
        specials_by_school = specials_by_school.drop_duplicates(subset=['专业名称', '招生年份'], keep='first')
        category_orders_by_score = specials_by_school['招生年份'].dropna().unique()
        category_orders_by_score = sorted([int(year) for year in category_orders_by_score])

        # #获取实际数据中的专业数量. 注意：这里获取的是去重后的专业数
        n_categories = specials_by_school['专业名称'].nunique()

        # #--------------------------------------------------------------------------------------
        # #按录取分数线绘制统计分析图表
        fig_special_by_score = px.histogram(
            specials_by_school,
            x='专业名称',           # X轴：专业
            y='分数线',            # Y轴：分数
            color='招生年份',       # 颜色：年份（自动生成图例）
            barmode='group',        # 关键：设置为 'group' 实现并排显示
            # text='录取分数线',     # 在柱子上方显示具体分数
            # title=f'{school_choice} - 各专业历年录取数据对比',
            color_discrete_sequence=px.colors.qualitative.Set1,  # 可选，设置颜色主题
            opacity=0.7,
            category_orders={'招生年份': category_orders_by_score}
        )
        # #自定义鼠标悬停显示效果               
        fig_special_by_score.update_traces(
            # hovertemplate 是自定义显示的模板
            # <extra></extra> 用于隐藏默认显示在第二行的显示数据，让界面更干净
            hovertemplate=(
                "<b>招生年份: %{data.name}</b><br>"
                "专业名称: %{x}<br>"
                "分数线：%{y}<br>"
                "<extra></extra>"
            ),
            # # 通过update_traces设置柱子样式，可以选择柱子进行样式设置
            # marker=dict(cornerradius=3), 
            # selector=dict(name='2023')  # 可以选择柱子进行设置
        )
        # #自定义y轴标签文字显示
        fig_special_by_score.update_layout(
            showlegend=True,
            bargroupgap = 0.1,    # 设置同组柱子间距
            # 通过update_layout设置柱子样式，所有柱子样式全局设置
            barcornerradius=3, 
            yaxis_title='分数线'
        )

        if n_categories < 3:
                fig_special_by_score.update_xaxes(range=[-2.5, 2.5])

        st.plotly_chart(fig_special_by_score)

    # # ----------------------------------------------------------------------------------------------
    # # 按名次展示逻辑进行数据计算与图表展示
    elif special_analysis_type == '按名次':
        # #----------------------------------------------------------------------------------------------
        # 进行去重
        # subset=['专业名称', '招生年份'] 指定根据这两列来判断是否重复
        # keep='first' 表示保留排序后的第一条（也就是分数最高的那一条）
        specials_by_school = specials_by_school.sort_values('名次排位', ascending=True)
        specials_by_school = specials_by_school.drop_duplicates(subset=['专业名称', '招生年份'], keep='first')
        category_orders_by_rank = specials_by_school['招生年份'].dropna().unique()
        category_orders_by_rank = sorted([int(year) for year in category_orders_by_rank])

        # #获取实际数据中的专业数量. 注意：这里获取的是去重后的专业数
        n_categories = specials_by_school['专业名称'].nunique()

        # #-------------------------------------------------------------------------------------------
        # #按照名次排位绘制统计分析图表
        fig_special_by_rank = px.histogram(
            specials_by_school,
            x='专业名称',           # X轴：专业
            y='名次排位',           # Y轴：名次排位
            color='招生年份',       # 颜色：年份（自动生成图例）
            barmode='group',        # 关键：设置为 'group' 实现并排显示
            # text='录取分数线',     # 在柱子上方显示具体分数
            # title=f'{school_choice} - 各专业历年录取数据对比',
            color_discrete_sequence=px.colors.qualitative.Set1,  # 可选，设置颜色主题
            opacity=0.7,
            category_orders={'招生年份': category_orders_by_rank}
        )
        # #自定义鼠标悬停显示效果               
        fig_special_by_rank.update_traces(
            # hovertemplate 是自定义显示的模板
            # <extra></extra> 用于隐藏默认显示在第二行的显示数据，让界面更干净
            hovertemplate=(
                "<b>招生年份: %{data.name}</b><br>"
                "专业名称: %{x}<br>"
                # "名次排位：%{y}<br>"
                "名次排位：%{y:,.0f}<br>" 
                "<extra></extra>"
            ),
            # # 通过update_traces设置柱子样式，可以选择柱子进行样式设置
            # marker=dict(cornerradius=3), 
            # selector=dict(name='2023')  # 可以选择柱子进行设置
        )
        # #自定义y轴标签文字显示
        fig_special_by_rank.update_layout(
            showlegend=True,
            bargroupgap = 0.1,      # 设置同组柱子间距
            # 通过update_layout设置柱子样式，所有柱子样式全局设置
            barcornerradius=3, 
            yaxis_title='名次排位'
        )

        if n_categories < 3:
                fig_special_by_rank.update_xaxes(range=[-2.5, 2.5])

        st.plotly_chart(fig_special_by_rank)
