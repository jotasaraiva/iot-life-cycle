import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from src import utils
import datetime
import uuid
import numpy as np
import json
from st_supabase_connection import SupabaseConnection, execute_query

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
    st.switch_page('Home.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')
    
# Layout
if st.session_state['authentication_status']:

    conn = st.connection("supabase", type=SupabaseConnection)
    rows = execute_query(conn.table("estoque").select("*"), ttl="5m")
    estq_data = pd.DataFrame(rows.data)

    with st.sidebar:
        flt_cliente = st.selectbox('Filtro de Clientes', tuple(utils.clientes), index=None)
        flt_status = st.selectbox('Filtro de Status', ('Estoque', 'Cliente', 'Remanufatura'), index=None)

    st.markdown('## Cadastro de Estoque')
    macs = st.text_area('MACs')

    nrows = len(macs.splitlines())
    status = pd.Series([np.nan] * nrows)
    cliente = pd.Series([np.nan] * nrows)
    data = datetime.datetime.today().strftime('%Y-%m-%d')
    origem = pd.Series([np.nan] * nrows)
    lote_recebimento = pd.Series([np.nan] * nrows)
    lote_treevia = pd.Series([np.nan] * nrows)
    defeito = pd.Series([False] * nrows)
    diag = pd.Series([np.nan] * nrows)

    status = st.selectbox('Status', ('Estoque', 'Cliente', 'Remanufatura'), index=None)
    if status == 'Cliente':
        cliente = st.selectbox('Cliente', tuple(utils.clientes))
    elif status == 'Estoque':
        origem = st.radio('Origem', ('Fornecedor', 'Cliente'))
        if origem == 'Fornecedor':
            lote_receb = st.text_input('Lote de Recebimento')
            lote_treevia = st.text_input('Lote Interno')
        defeito = st.radio('Defeito', (True, False), index=1, format_func=utils.format_bool)
        if defeito:
            diag = st.selectbox('Diagnóstico', tuple(utils.problemas))

    new_data = pd.DataFrame({
            'macs': macs.splitlines(),
            'status': status,
            'cliente': cliente,
            'data': data,
            'origem': origem,
            'lote_recebimento': lote_recebimento,
            'lote_treevia': lote_treevia,
            'defeito': defeito,
            'diag': diag
        })

    records = json.loads(new_data.to_json(orient='records', date_format='iso'))

    if new_data.shape[0] != 0:
        st.markdown('Preview dos dados')
        st.dataframe(new_data, use_container_width=True, hide_index=True)

    cols = st.columns((.3,.3,.3))
    with cols[0]:
        st.button('Subir', on_click=utils.update_sensores, 
                  args=[records, conn], 
                  use_container_width=True, type='primary')

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')