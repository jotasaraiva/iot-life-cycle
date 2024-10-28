import streamlit as st

st.set_page_config(page_title="Treevia LC - Sobre")

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Dashboard.py')

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
with st.sidebar:
    st.image(name_path)