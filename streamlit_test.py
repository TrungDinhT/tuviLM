import streamlit as st

from src.agent.cung_analyzer import CungAnalyzer
from src.tuvi.birth import BirthTime
from src.tuvi.builder import Builder
import datetime as dt

from src.tuvi.database.database import ALL_COMPOSITIONS
from src.tuvi.search_tool import check_composition

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

st.sidebar.header("Ngày sinh theo lịch dương")

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
        cung_1=repr(tinhBan.map_cung["Tị"]),
        cung_2=repr(tinhBan.map_cung["Ngọ"]),
        cung_3=repr(tinhBan.map_cung["Mùi"]),
        cung_4=repr(tinhBan.map_cung["Thân"]),
        cung_5=repr(tinhBan.map_cung["Thìn"]),
        cung_6=repr(tinhBan.map_cung["Dậu"]),
        cung_7=repr(tinhBan.map_cung["Mão"]),
        cung_8=repr(tinhBan.map_cung["Tuất"]),
        cung_9=repr(tinhBan.map_cung["Dần"]),
        cung_10=repr(tinhBan.map_cung["Sửu"]),
        cung_11=repr(tinhBan.map_cung["Tý"]),
        cung_12=repr(tinhBan.map_cung["Hợi"]),
        common_info=common_info
    ), unsafe_allow_html=True)

# ---------------- Seach for element composition -------------

for compo in ALL_COMPOSITIONS:
    if check_composition(tinhBan, compo):
        st.markdown(f"Having : {compo.name}")

# Add position selection and analyze button
st.markdown("## Phân tích cung")

analyzer = CungAnalyzer()


# Get all available positions
available_positions = list(tinhBan.map_cung.keys())

# Multi-select box for choosing positions
selected_positions = st.multiselect(
    "Chọn các cung muốn phân tích:",
    options=available_positions,
    default=[]
)

# Analyze button
analyze_button = st.button("Phân tích các cung đã chọn")

# Only analyze when button is clicked and positions are selected
if analyze_button and selected_positions:
    for position in selected_positions:
        cung = tinhBan.map_cung[position]

        st.markdown(f"### Bình luận về cung {cung.role} ({position})")

        st.markdown(analyzer.analyze_cung(position, cung))

        st.markdown("---")
