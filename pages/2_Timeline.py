import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px
from src import utils

# Page config
st.set_page_config(page_title="Treevia LC - Timeline", layout='wide')

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
with st.sidebar:
    st.image(name_path)

# Custom CSS
st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
                button[title="View fullscreen"]{
                    visibility: hidden;}
                [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
                    gap: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Check authentication state
if 'authenticator' not in st.session_state:
    st.switch_page('Dashboard.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Dashboard.py')

# Layout
if st.session_state['authentication_status']:

    tl_data = pd.read_csv('data/timeline.csv')
    tl_data_group = tl_data.groupby(['data', 'status']).size().reset_index(name='count')

    bar = px.bar(tl_data_group, x='data', y='count', color='status', barmode='group', labels={'data': '', 'count': 'N° de Sensores', 'status': 'Status'})
    bar.update_layout(height=350, margin=dict(l=40, r=40, t=20, b=20))

    st.plotly_chart(bar, use_container_width=True)
    st.dataframe(tl_data, use_container_width=True, hide_index=True, height=280)

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Dashboard.py')

