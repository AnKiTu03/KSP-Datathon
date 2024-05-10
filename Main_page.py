from streamlit_option_menu import option_menu
import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np

with st.sidebar:
    selected = option_menu("Main Menu", ["DashBoard", 'MapView', 'Video Analysis', 'Victim Analysis', 'Feedback', 'Contact Us'], 
        icons=['bar-chart', 'radar', 'camera-reels', 'person-bounding-box', 'card-text', 'envelope-at'], menu_icon="cast", default_index=0,styles=
        {
        "icon": {"font-size": "32px"}, 
        "nav-link": {"font-size": "32px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"}})


if selected == 'DashBoard':

    cols = st.columns(4)
    with cols[0]:
        ui.card(title="Crime Report", content="45,231", description="+20.1%from last month",key="card1").render()
    with cols[1]:
        ui.card(title="Crime Solved  ", content="+2350", description="+18.1% fromlast month",key="card2").render()
    with cols[2]:
        ui.card(title="Cases Pending", content="+3,234", description="+19% from lastmonth",key="card3").render  ()
    with cols[3]:
        ui.card(title="Active Cases    ", content="+2350", description="+18.1% fromlast month", key="card4").render()
