import streamlit as st
from src import utils
import pathlib

# Configuração da página
st.set_page_config(page_title="Treevia LC - Sobre", layout='wide', page_icon='assets/favicon.ico')

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
with st.sidebar:
    st.image(name_path)

# CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
css_path = pathlib.Path(__file__).parents[1] / "assets" / "about_styles.css"
load_css(css_path)

# Checar estado de autenticação
if 'authenticator' not in st.session_state:
    st.switch_page('Home.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')

# Layout
if st.session_state['authentication_status']:

    # Ler arquivo markdown
    def read_md(path):
        file = pathlib.Path(__file__).parents[1] / path
        return file.read_text(encoding='utf-8')
    intro = read_md('assets/about.md')

    # Layout
    page = st.container()
    with page:
        st.markdown(intro)
        st.html('<br/>')

    # Logout
    utils.log_out()

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')