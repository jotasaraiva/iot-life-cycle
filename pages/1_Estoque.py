import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from src import utils
import datetime
import uuid
import numpy as np
import json
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
    estq_rows = execute_query(conn.table("estoque").select("*"), ttl="5m")
    estq_data = pd.DataFrame(estq_rows.data)
    tl_rows = execute_query(conn.table('timeline').select("*"), ttl="5m")
    tl_data = pd.DataFrame(tl_rows.data)

    st.markdown('## Cadastro de Estoque')
    macs = st.text_area('MACs')
    data = st.date_input('Data', format='DD/MM/YYYY')

    nrows = len(macs.splitlines())
    disable_button = True

    # formulário de cadastro de estoque
    status = st.segmented_control('Status', ('Cliente', 'Estoque','Remanufatura'), default=None)
    if status == 'Cliente':
        cliente = st.selectbox('Cliente', tuple(utils.clientes))
        defeito = False
    elif status == 'Estoque':
        origem = st.radio('Origem', ('Fornecedor', 'Cliente'))
        if origem == 'Fornecedor':
            lote_recebimento = st.text_input('Lote de Recebimento')
            lote_treevia = st.text_input('Lote Interno')
        defeito = st.radio('Defeito', (True, False), index=1, format_func=utils.format_bool)
        if defeito:
            diag = st.selectbox('Diagnóstico', tuple(utils.problemas))
    elif status == 'Remanufatura':
        defeito = False
    elif status == None:
        defeito = False

    def make_exist(vars):
        for var in vars:
            if var not in globals() or globals()[var] == '':
                globals()[var] = None

    make_exist(['cliente', 'lote_recebimento', 'lote_treevia', 'origem', 'diag', 'ciclo'])

    # validação de dados do formulário
    if macs != '':
        ciclo = None
        if status == 'Cliente':
            if cliente != '':
                disable_button = False
        if status == 'Estoque':
            if origem == 'Fornecedor':
                if lote_recebimento != None and lote_treevia != None:
                    if defeito:
                        if diag != None:
                            disable_button = False
                    elif not defeito:
                        disable_button = False
            if origem == 'Cliente':
                if defeito:
                        if diag != None:
                            disable_button = False
                elif not defeito:
                    disable_button = False
        if status == 'Remanufatura':
            disable_button = False

    new_data = pd.DataFrame({
            'macs': macs.splitlines(),
            'status': status,
            'cliente': cliente,
            'data': data,
            'origem': origem,
            'lote_recebimento': lote_recebimento,
            'lote_treevia': lote_treevia,
            'defeito': defeito,
            'diag': diag,
            'ciclo': ciclo
        })
    
    if status in ('Remanufatura', 'Cliente'):
        new_data['lote_recebimento'] = list([
            utils.get_last_values_by_date(tl_data, 'macs', mac, 'lote_recebimento', 'data')
            for mac in macs.splitlines()
        ])
        new_data['lote_treevia'] = list([
            utils.get_last_values_by_date(tl_data, 'macs', mac, 'lote_treevia', 'data')
            for mac in macs.splitlines()
        ])

    if origem != 'Fornecedor':
        new_data['ciclo'] = list([
            utils.get_last_values_by_date(tl_data, 'macs', mac, 'ciclo', 'data')
            for mac in macs.splitlines()
        ])
    else:
        new_data['ciclo'] = list([
            utils.get_last_values_by_date(tl_data, 'macs', mac, 'ciclo', 'data')
            for mac in macs.splitlines()
        ])


    records = json.loads(new_data.to_json(orient='records', date_format='iso'))
    if new_data.shape[0] != 0:
        st.markdown('Preview dos dados')
        st.dataframe(new_data, use_container_width=True, hide_index=True)
    
    cols = st.columns((.3,.3,.3))
    with cols[1]:
        button = st.button('Subir', on_click=utils.update_sensores, 
                  args=[records, conn], disabled=disable_button,
                  use_container_width=True, type='primary')
    if button:
        st.cache_data.clear()

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')