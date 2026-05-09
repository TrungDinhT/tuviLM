from __future__ import annotations

import datetime as dt

import streamlit as st

from src.refactored.context.prior import Gender, LaSoPrior
from src.refactored.la_so import LaSo
from src.refactored.view.builder import build_laso_view
from src.refactored.view.streamlit_adapter import render_laso_view_html


st.sidebar.header("Ngày sinh theo lịch dương")

date = st.sidebar.number_input("Ngày sinh:", min_value=1, max_value=31, value=4)
month = st.sidebar.number_input("Tháng sinh:", min_value=1, max_value=12, value=4)
year = st.sidebar.number_input("Năm sinh:", min_value=1, max_value=9999, value=1998)
hour = st.sidebar.number_input("Giờ Sinh:", min_value=0, max_value=23, value=8)
gender = st.sidebar.selectbox("Giới tính:", options=["M", "F"], index=0)
study_year = st.sidebar.number_input(
    "Năm xem:",
    min_value=1,
    max_value=9999,
    value=dt.datetime.now().year,
)

birth_time = dt.datetime(year, month, date, hour)
prior = LaSoPrior.from_solar_day(
    birth_time,
    Gender.MALE if gender == "M" else Gender.FEMALE,
)
la_so = LaSo.from_prior(prior)
view = build_laso_view(la_so, study_year=study_year)

st.markdown(
    render_laso_view_html(view),
    unsafe_allow_html=True,
)
