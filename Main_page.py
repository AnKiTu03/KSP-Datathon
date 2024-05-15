from streamlit_option_menu import option_menu
import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
from patrolling import patrolling_main
from victim import Victim_main
from forecast import forecast_main
from video import video_main

with st.sidebar:
    selected = option_menu("Main Menu", ['DashBoard', 'MapView', 'Video Analysis', 'Victim Analysis','Forecast', 'Feedback', 'Contact Us' , 'Sign Up' , 'Sign In'], 
        icons=['bar-chart', 'radar', 'camera-reels', 'person-bounding-box','graph-up-arrow','card-text', 'envelope-at'], menu_icon="cast", default_index=0,styles=
        {
        "icon": {"font-size": "24px"}, 
        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px",  "--hover-color": "#48A6EE" , "margin-top" : "10px"},
        "nav-link-selected": {"background-color": "#48A6EE" , "font-weight" : "100"}})


if selected == 'DashBoard':

    st.write(":house: / DashBoard")
    cols = st.columns([0.7, 0.3])
    with cols[0]:
     st.write("**Dashboard**")
    with cols[1]:
        cols = st.columns(2)
        with cols[0]:
         st.markdown('<input style="width: 150px; height: 25px; outline: none; padding: 5px; border: 1px solid white ; border-radius: 5px; background-color: black;" type="text" placeholder="Search here">', unsafe_allow_html=True)

    cols = st.columns(4)
    with cols[0]:
        ui.card(title="Crime Report", content="45,231", description="+20.1%from last month",key="card1").render()
    with cols[1]:
        ui.card(title="Crime Solved  ", content="+2350", description="+18.1% fromlast month",key="card2").render()
    with cols[2]:
        ui.card(title="Cases Pending", content="+3,234", description="+19% from lastmonth",key="card3").render  ()
    with cols[3]:
        ui.card(title="Active Cases    ", content="+2350", description="+18.1% fromlast month", key="card4").render()

elif selected == 'MapView':
    patrolling_main()

elif selected == 'Victim Analysis':
    Victim_main()

elif selected == 'Forecast':
    forecast_main()

elif selected == 'Video Analysis':
    video_main()