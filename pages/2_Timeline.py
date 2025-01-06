import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px
from src import utils
from st_supabase_connection import SupabaseConnection, execute_query
import pathlib

# Page config
st.set_page_config(page_title="Treevia LC - Timeline", layout='wide')

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
with st.sidebar:
    st.image(name_path)

# CSS config
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
css_path = pathlib.Path(__file__).parents[1] / "assets" / "stock_styles.css"
load_css(css_path)

# Check authentication state
if 'authenticator' not in st.session_state:
    st.switch_page('Home.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')

# Layout
if st.session_state['authentication_status']:

    conn = st.connection("supabase", type=SupabaseConnection)
    rows = execute_query(conn.table("timeline").select("*"), ttl="5m")
    time_data = pd.DataFrame(rows.data)

    st.dataframe(time_data, use_container_width=True, hide_index=True, height=625)

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')

