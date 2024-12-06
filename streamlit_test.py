import streamlit as st

from src.tuvi.birth import BirthTime
from src.tuvi.tinh_ban import TinhBan
from src.tuvi.types import LIST_DIA_CHI, LIST_THIEN_CAN
from src.tuvi.builder import Builder
import datetime as dt

# Define the HTML and CSS for the table
html_table_template = """
<style>
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .custom-table, .custom-table th, .custom-table td {{
        border: 1px solid black;
    }}
    .custom-table td {{
        width: 1000px;
        height: 150px;
        text-align: center;
        vertical-align: middle;
    }}
    .merged-cell {{
        grid-column: span 2;
        grid-row: span 2;
    }}
</style>

<table class="custom-table"; table-layout: auto;>
    <tr>
        <td style='vertical-align: top; padding: 5px;>{cung_1}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_2}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_3}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_4}</td>
    </tr>
    <tr>
        <td style='vertical-align: top; padding: 5px;>{cung_5}</td>
        <td class="merged-cell" rowspan="2" colspan="2">{common_info}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_6}</td>
    </tr>
    <tr>
        <td style='vertical-align: top; padding: 5px;>{cung_7}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_8}</td>
    </tr>
    <tr>
        <td style='vertical-align: top; padding: 5px;>{cung_9}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_10}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_11}</td>
        <td style='vertical-align: top; padding: 5px;>{cung_12}</td>
    </tr>
</table>
"""

st.sidebar.header("Ngày sinh theo lịch âm")

date = st.sidebar.number_input("Ngày sinh:", min_value=1, max_value=31, value=4)
month = st.sidebar.number_input("Tháng sinh:", min_value=1, max_value=12, value=4)
year = st.sidebar.number_input("Năm sinh:", min_value=1, max_value=9999, value=1998)
hour = st.sidebar.number_input("Giờ Sinh:", min_value=0, max_value=23, value=8)
gender = st.sidebar.selectbox("Giới tính:", options=["M", "F"], index=0)

birthTime = dt.datetime(year, month, date, hour)

birthTime = BirthTime.from_solar_day(birthTime, gender)

print(birthTime)

builder = Builder()

tinhBan = builder.build(birthTime)

common_info = f"Cục : {tinhBan.cuc.name} cục.<br> Giờ sinh : {birthTime}"

# Display the HTML table in Streamlit
st.markdown(html_table_template.format(
        cung_1=repr(tinhBan.map_cung["Ti"]),
        cung_2=repr(tinhBan.map_cung["Ngo"]),
        cung_3=repr(tinhBan.map_cung["Mui"]),
        cung_4=repr(tinhBan.map_cung["Than"]),
        cung_5=repr(tinhBan.map_cung["Thin"]),
        cung_6=repr(tinhBan.map_cung["Dau"]),
        cung_7=repr(tinhBan.map_cung["Mao"]),
        cung_8=repr(tinhBan.map_cung["Tuat"]),
        cung_9=repr(tinhBan.map_cung["Dan"]),
        cung_10=repr(tinhBan.map_cung["Suu"]),
        cung_11=repr(tinhBan.map_cung["Ty"]),
        cung_12=repr(tinhBan.map_cung["Hoi"]),
        common_info=common_info
    ), unsafe_allow_html=True)


print(sum(len(cung.phuTinh) + len(cung.chinhTinh) for cung in tinhBan.map_cung.values()))
