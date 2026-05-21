# -*- coding: utf-8 -*-

# 导入标准模块
from typing import cast, Any

# 导入第三方模块
import plotly.express as px
import pandas as pd
import streamlit as st


# 绘制学校各省份数量分布地图
def school_distribute_map(schools, china_provinces_geo):
        
    # #计算每个省份的高校数量，返回高校数量dataframe
        province_school_counts = (
            schools['省份']
            .value_counts()
            .rename_axis('省份')      # 给索引命名（可选，但推荐）
            .reset_index(name='高校数量')  # 直接指定新列名
        )

        # #合并geojson文件中省份，确保dataframe数据省份的完整性
        provinces_name_geo = [feature['properties']['name'] for feature in china_provinces_geo['features']]
        full_province_counts = pd.DataFrame({'省份': provinces_name_geo}).merge(province_school_counts, on='省份', how='left')
        full_province_counts['高校数量'] = full_province_counts['高校数量'].fillna(0)
        full_province_counts['高校数量'] = full_province_counts['高校数量'].astype(int)

        map_fig = px.choropleth_map(
            full_province_counts,
            geojson=china_provinces_geo,
            locations='省份',
            featureidkey="properties.name",  # GeoJSON 中存储省份名称的字段，可能是 'name' 或 'NAME'
            color="高校数量",
            color_continuous_scale=px.colors.sequential.Blues,
            hover_name='省份',
            hover_data=['高校数量'],
            custom_data=['高校数量'],
        )

        map_fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' + '高校数量: %{customdata[0]}' + '<extra></extra>'
        )

        map_fig.update_layout(
            map={
                'style': 'carto-positron',
                'zoom': 2.5,
                'center': {'lat': 37.8, 'lon': 104.2},
            },
            margin={"r":0,"t":0,"l":0,"b":0}   # 边距
        )

        event_provinces_map = st.plotly_chart(map_fig, width='stretch', height=370, on_select='rerun')
        event_provinces_map = cast(Any, event_provinces_map)

        return event_provinces_map