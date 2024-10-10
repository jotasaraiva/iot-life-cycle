import streamlit as st

st.set_page_config(page_title="Treevia LC - Timeline")

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
with st.sidebar:
    st.image(name_path)