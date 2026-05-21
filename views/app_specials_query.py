# -*- coding: utf-8 -*-

# #导入标准模块
from typing import cast, Any

# #导入第三方模块
import streamlit as st

# #导入自定义模块
from dataset import (
    load_data_schools,load_data_specialgroups
)
from settings import (
    PROVINCE_NAME_MAPPING, 
    set_divider_style, 
    set_popover_style,
    set_pagetop_style,
    set_navigation_style,
    set_alternating_colors
) 
from special_schools_query import build_special_schools_show

# ###############################################################################
# 设置CSS样式
# ###############################################################################
set_divider_style()
set_popover_style()
set_pagetop_style()
set_navigation_style()

# 初始化会话状态变量data_loaded， 在数据装载之前初始化为False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# 设置全局页面样式
st.set_page_config(
    page_title="高考志愿填报智能推荐系统",
    # page_icon="🎓",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
                st.write('加载高校综合信息中... (1/2)')
                raw_schools = load_data_schools()
                st.write('加载专业组录取信息中... (2/2)')
                raw_specialgroups = load_data_specialgroups()
            placeholder.empty()
        except Exception as e:
            placeholder.error(f"⚠️数据文件加载失败!") 
            raise e
            st.stop()
        
        st.session_state.data_loaded = True

    else:
        raw_schools = load_data_schools()
        raw_specialgroups = load_data_specialgroups()
    
    return raw_schools, raw_specialgroups

if __name__ == '__main__':

    # ###################################################################################################
    # 初始化数据
    raw_schools, raw_specialgroups = init_data()
    clean_specialgroups = raw_specialgroups.copy()
    # 将省份名称从简称改为全称
    clean_specialgroups['省份'] = clean_specialgroups['省份'].map(PROVINCE_NAME_MAPPING)

    # #####################################################################################################
    # 初始化侧边栏组件与组件数据
    with st.sidebar:
        with st.container(gap='xxsmall'):
            st.subheader(':material/search: 专业查询助手')
            # st.markdown("""
            # <div style="font-size: 1.1rem; opacity: 1.0; text-align: left; font-weight: bold; margin-bottom: 1rem;">
            #     专业查询助手
            # </div>
            # """, unsafe_allow_html=True)

            st.divider()
            # 按照2025年设置专业进行查询分析 --> 最近年份设置专业
            clean_specialgroups = clean_specialgroups[clean_specialgroups['招生年份'] == 2025]
            # 根据学校省份进行筛选
            province_all = sorted(clean_specialgroups['省份'].dropna().unique())
            province_options = ['不限'] + list(province_all)
            province_choice = st.selectbox('学校省份', options=province_options, index=0)
            if province_choice != '不限':
                clean_specialgroups = clean_specialgroups[clean_specialgroups['省份'] == province_choice]

            # 根据选科类型进筛选数据
            subject_choice = st.selectbox('选科类型', options=['物理类', '历史类'], index=0)
            clean_specialgroups = clean_specialgroups[clean_specialgroups['选科类型'] == subject_choice]

            # 根据招生类型筛选数据
            zslx_types = sorted(clean_specialgroups['招生类型'].dropna().unique())
            zslx_options = ['不限'] + list(zslx_types)
            zslx_default_index = zslx_options.index('普通类')
            zslx_choice = st.selectbox('招生类型', options=zslx_options, index=zslx_default_index)
            clean_specialgroups = clean_specialgroups[clean_specialgroups['招生类型(专业组补充)'] == zslx_choice]

            # 计算所有专业类别
            special_types = sorted(clean_specialgroups['二级分类'].dropna().unique())
            special_type_choice = st.selectbox('专业类型', options=list(special_types), index=10)
            
            # 根据专业类别，计算该专业类别下的所有专业子类
            specialgroups_by_type = clean_specialgroups[clean_specialgroups['二级分类'] == special_type_choice]
            special_subtypes = sorted(specialgroups_by_type['三级分类'].dropna().unique())
            special_subtype_choice = st.selectbox('专业子类', options=list(special_subtypes), index=0)

    # ##################################################################################
    # 定义主页面 
    st.markdown(
        f"##### :material/shadow: 全国高校专业信息数据查询结果 ",
        unsafe_allow_html=True
    )

    st.divider()
    specials = clean_specialgroups[(clean_specialgroups['二级分类'] == special_type_choice) & (clean_specialgroups['三级分类'] == special_subtype_choice)]
    specials_by_group = specials.groupby('专业名称').agg({
        '录取线': ['min', 'max'],
        '名次排位': ['max', 'min'],
        '招生人数': 'sum'
    }).reset_index()

    specials_by_group.columns = ['专业名称', '最低录取线', '最高录取线', '最低名次排位', '最高名次排位', '招生人数总数']
    
    # 设置表格斑马纹效果
    styled_specials_by_group = (
        specials_by_group
        .style
        .apply(set_alternating_colors, axis=None)
    )

    # 专业列表标题，呈现专业类别与专业子类
    st.markdown(f'###### :material/article: {special_type_choice} - {special_subtype_choice}')
    event_special_select = st.dataframe(
        styled_specials_by_group,
        hide_index=True,
        on_select='rerun',
        selection_mode='single-row'
    )

    event_special_select = cast(Any, event_special_select)
    #event_df为选择'高校列表'dataframe的事件响应数据
    if event_special_select and event_special_select.selection.rows:
        rows_selected = event_special_select.selection.rows
        # --------------------------------------------------------------------
        # 从展示的dataframe中筛选出所选学校的信息
        special_row_selected = specials_by_group.iloc[rows_selected]
        special_name = special_row_selected.squeeze()['专业名称']
        schools_by_special = clean_specialgroups[clean_specialgroups['专业名称'] == special_name]
        school_nums = schools_by_special['学校名称'].dropna().unique()

        # popover组件用于展示该专业所开设的院校，具体包括院校名称，最低录取线，招生人数等
        popover_label= f'【:red[{special_name}]】专业开设院校(✅:red[{len(school_nums)}] 所), 点击查看详情......'
        with st.popover(label=popover_label, width='stretch'):
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
                '三级分类',
                '招生类型(专业组补充)'
            ]
            special_school_all = schools_by_special[colunms_required_all]
            special_school_all = special_school_all.rename(columns={'二级分类': '专业类别', '三级分类': '专业子类'})
            special_school_show = special_school_all.copy()
            special_school_show['学制年数'] = special_school_show['学制年数'].replace({'3': '三年', '4': '四年', '5': '五年', '8': '八年'})
            # 页面显示数据按照录取线进行降序排列
            special_school_show.sort_values(by='录取线', ascending=False, inplace=True)
            if len(special_school_show) != 0:
                # # 计算该专业所属的专业类别与专业子类，可以使用sidebar侧边栏的选项作为专业类别与子类
                # # sidebar侧边栏对应的专业类别与子类变量为: special_type_choice, special_subtype_choice
                # special_type = special_school_all.iloc[0]['专业类别']
                # special_subtype = special_school_all.iloc[0]['专业子类']
                # 招生批次去重后的种类
                show_batch = list(special_school_show['招生批次'].dropna().unique())
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
                    st.markdown(f'<h6 style="color: #1c82e1;">{special_name}</h6>', unsafe_allow_html=True)
                    st.caption(f'{special_type_choice} - {special_subtype_choice}')
                with show_col2:
                    batch_selected = st.selectbox(
                        label='选择招生批次',
                        options=show_options,
                        index=default_index,
                        label_visibility='collapsed',
                    )
                if batch_selected != '不限':
                    special_school_show = special_school_show[special_school_show['招生批次'] == batch_selected]    
                    # st.dataframe(specialgroups_show, width='stretch', hide_index=True)
                build_special_schools_show(special_school_show)
            else:
                st.info(f':information_source: :blue[截至2025年, 院校已取消 {special_name} 专业设置......]')

    else:
        st.info(':information_source: :blue[想要查看某个专业:orange[【开设院校】]详细校信息，请在上面"专业列表"中进行勾选......]')