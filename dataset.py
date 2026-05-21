# -*- coding: utf-8 -*-

# #导入python标准模块
import json
import sqlite3

# #导入第三方模块
import streamlit as st
import pandas as pd


# 1. 数据文件路径，下面数据仅包含物理类数据
# file_path_excel = './data/广东省高考数据 20260409.xlsx'
# # 2. app_recommend v2版本调用数据，包括物理类与历史类所有数据，不包括最新爬取的2025年专业分数与名次数据
# file_path_excel = './data/广东省高考数据 ALL 20260426.xlsx'
# # 3. app_recommend v3版本调用数据，合并进最新爬取的2025年专业专业分数与名次数据
# file_path_excel = './data/广东省高考数据 ALL 20260518.xlsx'

# 读取数据库版本
conn = sqlite3.connect('./data/ncee.db')

# -------------------------------------------------------------------
# 加载广东省物理类高考各高校专业录取数据，在streamlit应用中使用缓存
# 数据清洗，筛选如下列数据:
# year, school_name, f985, f211, dual_class,  nature, level, province, city
# sp_name, spname, min, min_section, lq_num
# level1_name, level2_name, level3_name, zslx_name, local_batch_name 
# --------------------------------------------------------------------
@st.cache_data
def load_data_specials():
    # 定义筛选保留的列
    columns_reserved = [
        '选科类型',
        'ID',
        '招生年份',
        '学校名称',
        'f985',
        'f211',
        '双一流',
        '办学体制',
        '办学层次',
        '省份',
        '城市',
        '专业名称',
        '专业详情',
        '最低分',
        '名次排位',
        '招生人数',
        '一级分类',
        '二级分类',
        '三级分类',
        '招生类型',
        '招生批次'
    ]

    try:
        # # 读取excel文件版本
        # df = pd.read_excel(file_path_excel, sheet_name='学校专业录取线')
        # 读取数据库版本
        df = pd.read_sql("SELECT * FROM specials", conn)

        df = df[columns_reserved]
        # df['招生人数'] = df['招生人数'].astype('str')
        df['招生人数'] = pd.to_numeric(df['招生人数'], errors='coerce')
        df['招生人数'] = df['招生人数'].astype('Int64')
        df['最低分'] = pd.to_numeric(df['最低分'], errors='coerce')
        df['最低分'] = df['最低分'].astype('Int64')
        df['名次排位'] = pd.to_numeric(df['名次排位'], errors='coerce')
        df['名次排位'] = df['名次排位'].astype('Int64')
        df.dropna(subset=['最低分', '名次排位'], how='all', inplace=True)
        df.rename(columns={'f985': 'F985', 'f211': 'F211', '最低分': '录取线'}, inplace=True)

        return df
    except Exception as e:
        raise e
    

# -----------------------------------------------------------------------------
# 加载全国高校数据信息，包括近3年物理类最低录取分数线等信息
# 数据清洗，筛选如下列数据:
# 学校名称，软科排名，f985,f211,双一流，2023分数，2024分数，2025分数，办学类型，
# 办学体制，办学层次，隶属关系，省份，城市，创建时间
# -----------------------------------------------------------------------------
@st.cache_data
def load_data_schools():
    # 定义筛选保留的列
    columns_reserved = [
        '选科类型',
        'ID',
        '学校名称',
        '软科排名',
        'f985',
        'f211',
        '双一流',
        '保研率',
        '2022分数线',
        '2023分数线',
        '2024分数线',
        '2025分数线',
        '办学类型',
        '办学体制',
        '办学层次',
        '隶属关系',
        '省份',
        '城市',
        '创建时间'
    ]

    try:
        # # 读取excel文件版本
        # df = pd.read_excel(file_path_excel, sheet_name='学校详细信息')
        # 读取数据库版本
        df = pd.read_sql("SELECT * FROM schools", conn)
        
        df = df[columns_reserved]
        df['软科排名'] = pd.to_numeric(df['软科排名'], errors='coerce')
        df['软科排名'] = df['软科排名'].astype('Int64')
        df['2022分数线'] = pd.to_numeric(df['2022分数线'], errors='coerce')
        df['2022分数线'] = df['2022分数线'].astype('Int64')
        df['2023分数线'] = pd.to_numeric(df['2023分数线'], errors='coerce')
        df['2023分数线'] = df['2023分数线'].astype('Int64')
        df['2024分数线'] = pd.to_numeric(df['2024分数线'], errors='coerce')
        df['2024分数线'] = df['2024分数线'].astype('Int64')
        df['2025分数线'] = pd.to_numeric(df['2025分数线'], errors='coerce')
        df['2025分数线'] = df['2025分数线'].astype('Int64')
        df.rename(columns={'f985': 'F985', 'f211': 'F211'}, inplace=True)

        return df
    except Exception as e:
        raise e
    

# ------------------------------------------------------------------------
# 加载中国省份地理数据 china_provinces.geojson
# ------------------------------------------------------------------------
@st.cache_data
def load_china_provinces_geojson():
    with open("./data/geo/china_provinces.geojson", "r", encoding="utf-8") as f:
        china_provinces_geojson = json.load(f)
    return china_provinces_geojson


# -------------------------------------------------------------------
# 加载广东省物理类高考各高校专业组录取数据，在streamlit应用中使用缓存
# 数据清洗，筛选如下列数据:
# year, school_name, f985, f211, dual_class,  nature, level, province, city
# sp_name, spname, min, min_section, lq_num
# level1_name, level2_name, level3_name, zslx_name, local_batch_name 
# --------------------------------------------------------------------
@st.cache_data
def load_data_specialgroups():
    # 定义筛选保留的列
    columns_reserved = [
        '选科类型',
        'ID',
        '招生年份',
        '学校名称',
        'f985',
        'f211',
        '双一流',
        '办学体制',
        '办学层次',
        '省份',
        '城市',
        '专业名称',
        '专业详情',
        '录取线',
        '名次排位',
        '招生人数',
        '一级分类',
        '二级分类',
        '三级分类',
        '招生批次',
        '招生类型',
        '学制年数',
        '学费',
        '招生类型(专业组补充)'
    ]
    try:
        # # 读取excel文件版本
        # df = pd.read_excel(file_path_excel, sheet_name='学校专业组录取线')
        # 读取数据库版本
        df = pd.read_sql("SELECT * FROM specialgroups", conn)

        df = df[columns_reserved]
        df['招生人数'] = pd.to_numeric(df['招生人数'], errors='coerce')
        df['招生人数'] = df['招生人数'].astype('Int64')
        df['录取线'] = pd.to_numeric(df['录取线'], errors='coerce')
        df['录取线'] = df['录取线'].astype('Int64')
        df['名次排位'] = pd.to_numeric(df['名次排位'], errors='coerce')
        df['名次排位'] = df['名次排位'].astype('Int64')
        df.rename(columns={'f985': 'F985', 'f211': 'F211'}, inplace=True)

        return df
    except Exception as e:
        raise e


if __name__ == '__main__':
    pass

