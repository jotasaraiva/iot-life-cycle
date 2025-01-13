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
    time_data['data'] = pd.to_datetime(time_data['data']).dt.date

    lotes_recebimento = time_data['lote_recebimento'].dropna().unique()
    lotes_treevia = time_data['lote_treevia'].dropna().unique()
    clientes = time_data['cliente'].dropna().unique()
    max_date = time_data['data'].max()
    min_date = time_data['data'].min()

    with st.sidebar:
        flt_cliente = st.selectbox('Cliente', clientes, index=None)
        flt_lote_rec = st.selectbox('Lote de Recebimento', lotes_recebimento, index=None)
        flt_lote_trv = st.selectbox('Lote Interno', lotes_treevia, index=None)
        flt_date = st.slider('Intervalo', min_value=min_date, max_value=max_date, format='DD/MM/YYYY', value=(min_date, max_date))

    agg_data = utils.avg_fail_time(time_data)

    st.dataframe(time_data, use_container_width=True, hide_index=True)
    st.dataframe(agg_data, use_container_width=True, hide_index=True)

    bar_data = (
        time_data
        .groupby(['status', 'data'])
        .size()
        .reset_index(name='counts')
        .sort_values(by='data')
    )   

    #fig = px.bar(bar_data, x='data', y='counts', orientation='h', color='status', barmode='group')

    st.dataframe(bar_data)
    
    # Logout
    st.session_state['authenticator'].logout(location='sidebar')

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')
