import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from src import utils
from st_supabase_connection import SupabaseConnection, execute_query

st.set_page_config(page_title="Treevia LC - Diagnóstico")

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')

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
        </style>
        
        """, unsafe_allow_html=True)

# Check authentication state
if 'authenticator' not in st.session_state:
    st.switch_page('Home.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')

# Layout
if st.session_state['authentication_status']:

    conn = st.connection("supabase", type=SupabaseConnection)
    rows = execute_query(conn.table("estoque").select("*"), ttl="5m")
    estq_data = pd.DataFrame(rows.data)

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')