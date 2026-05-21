# -*- coding: utf-8 -*-

# #导入第三方模块
import streamlit as st

# #导入自定义模块
from dataset import (
    load_data_specials, load_data_schools, load_china_provinces_geojson,load_data_specialgroups
)



if __name__ == '__main__':

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

    # ----------------------------------------------------------------------------
    # 加载数据，加载失败streamlit应用停止运行
    # ----------------------------------------------------------------------------
    # 创建一个占位容器，用于在加载时显示消息，加载完成后清空或替换

    if not st.session_state.data_loaded:

        placeholder = st.empty()

        try:
            with placeholder.status('🚀 广东省高考数据加载中，请稍后...'):
                st.write('加载专业录取信息中... (1/4)')
                df_specials = load_data_specials()
                st.write('加载高校综合信息中... (2/4)')
                df_schools = load_data_schools()
                st.write('加载全国地图数据中... (3/4)')
                china_provinces_geojson = load_china_provinces_geojson()
                st.write('加载专业组录取信息中... (4/4)')
                df_specialgroups = load_data_specialgroups()
            placeholder.empty()
        except Exception as e:
            placeholder.error(f"⚠️数据文件加载失败!") 
            raise e
            st.stop()
        
        st.session_state.data_loaded = True
        # st.balloons()

    else:
        df_specials = load_data_specials()
        df_schools = load_data_schools()
        china_provinces_geojson = load_china_provinces_geojson()
        df_specialgroups = load_data_specialgroups()

    page_recommend = st.Page('./views/app_recommend.py', title=':rainbow[**志愿填报智能推荐**]', icon=':material/home:', url_path='recommend')
    page_schools = st.Page('./views/app_schools.py', title=':rainbow[**全国高校综合信息**]', icon=':material/menu:',url_path='school')
    page_admission = st.Page('./views/app_admission.py', title=':rainbow[**高校专业录取信息**]', icon=':material/menu:', url_path='admission')
    page_specials_query = st.Page('./views/app_specials_query.py', title=':rainbow[**高校专业信息查询**]', icon=':material/menu:', url_path='major')

    pg = st.navigation(pages=[ page_recommend, page_schools, page_admission, page_specials_query])

    pg.run()

  