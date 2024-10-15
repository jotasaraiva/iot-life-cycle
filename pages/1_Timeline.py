import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
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
        </style>
        
        """, unsafe_allow_html=True)

# Check authentication state
if 'authenticator' not in st.session_state:
    st.switch_page('Estoque.py')

# Layout
if st.session_state['authentication_status']:
    # Logout
    st.session_state['authenticator'].logout(location='sidebar')

    # API calls
    exch = utils.call_exchange()

    # Exchange data
    exch_data = pd.DataFrame(exch.json()['result'])
    exch_data['date'] = pd.to_datetime(exch_data['exch_ts_unix_timestamp'], unit='ms')

    # Testing
    st.markdown('## Teste Timeline')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Estoque.py')

