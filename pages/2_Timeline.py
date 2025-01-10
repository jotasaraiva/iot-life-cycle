import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np
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
css_path = pathlib.Path(__file__).parents[1] / "assets" / "tl_styles.css"
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

    lotes_recebimento = time_data['lote_recebimento'].dropna().unique()
    lotes_treevia = time_data['lote_treevia'].dropna().unique()
    max_date = utils.convert_date(time_data['data'].max())
    min_date = utils.convert_date(time_data['data'].min())

    with st.sidebar:
        st.selectbox('Cliente', utils.clientes, index=None)
        st.selectbox('Lote de Recebimento', lotes_recebimento, index=None)
        st.selectbox('Cliente', lotes_treevia, index=None)
        st.slider('Intervalo', min_value=min_date, max_value=max_date, format='DD/MM/YYYY', value=(min_date, max_date))

    time_data['retorno'] = np.where((time_data['status'] == 'Estoque') & (time_data['origem'] == 'Fornecedor'), 'inicio', None)
    time_data['retorno'] = np.where((time_data['status'] == 'Estoque') & (time_data['origem'] == 'Cliente'), 'fim', time_data['retorno'])

    st.dataframe(time_data)

    def calculate(group):
        return utils.convert_date(group['data'].max()) - utils.convert_date(group['data'].min())

    test = time_data.groupby('macs').apply(calculate, include_groups=False)
    st.text(test)

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')
