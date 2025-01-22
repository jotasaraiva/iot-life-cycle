import streamlit as st
import pandas as pd
from src import utils
import json
from st_supabase_connection import SupabaseConnection, execute_query
import pathlib

# Configuração da página
st.set_page_config(page_title="Treevia LC - Cadastro", layout='wide', page_icon='assets/favicon.ico')

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
css_path = pathlib.Path(__file__).parents[1] / "assets" / "stock_styles.css"
load_css(css_path)

# Checar estado de autenticação
if 'authenticator' not in st.session_state:
    st.switch_page('Home.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')
    
# Layout
if st.session_state['authentication_status']:

    # Query da database
    conn = st.connection("supabase", type=SupabaseConnection)
    estq_rows = execute_query(conn.table("estoque").select("*"), ttl="5m")
    estq_data = pd.DataFrame(estq_rows.data)
    tl_rows = execute_query(conn.table('timeline').select("*"), ttl="5m")
    tl_data = pd.DataFrame(tl_rows.data)

    st.markdown('## Cadastro de Estoque')

    # Formulário de cadastro
    form = st.container(border=True)
    with form:
        # Input de MACs, data e status
        macs = st.text_area('MACs')
        data = st.date_input('Data', format='DD/MM/YYYY')
        status = st.segmented_control('Status', ('Cliente', 'Estoque','Remanufatura', 'Descarte'), default=None)

        # Renderização dinâmica do formulário
        nrows = len(macs.splitlines())
        disable_button = True
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
        elif status == 'Descarte':
            defeito = False
        elif status == None:
            defeito = False

    # Declarar variáveis que não foram preenchidas anteriormente
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
        if status == 'Remanufatura' or 'Descarte':
            disable_button = False

    # Construção dos novos registros para o banco
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
    
    # Resgatar ou limpar lote de recebimento e interno
    if (status in ('Remanufatura', 'Cliente', 'Descarte')) or (status == 'Estoque' and origem == 'Cliente'):
        new_data['lote_recebimento'] = list([
            utils.get_batch(tl_data, 'macs', mac, 'lote_recebimento', 'data')
            for mac in macs.splitlines()
        ])
        new_data['lote_treevia'] = list([
            utils.get_batch(tl_data, 'macs', mac, 'lote_treevia', 'data')
            for mac in macs.splitlines()
        ])

    # Resgatar ou incrementar ciclo
    if status == 'Estoque' and origem == 'Fornecedor':
        new_data['ciclo'] = list([
            utils.get_cycle(tl_data, 'macs', mac, 'ciclo', 'data', 1)
            for mac in macs.splitlines()
        ])
    else:
        new_data['ciclo'] = list([
            utils.get_cycle(tl_data, 'macs', mac, 'ciclo', 'data')
            for mac in macs.splitlines()
        ])

    # Criar JSON
    records = json.loads(new_data.to_json(orient='records', date_format='iso'))

    # Pré-visualização dos dados
    if new_data.shape[0] != 0:
        st.markdown('Preview dos dados')
        st.dataframe(new_data, use_container_width=True, hide_index=True)
    
    # Upload dos dados
    cols = st.columns((.3,.3,.3))
    with cols[1]:
        button = st.button('Cadastrar', on_click=utils.update_sensores, 
                  args=[records, conn], disabled=disable_button,
                  use_container_width=True, type='primary')
    if button:
        st.cache_data.clear()
    st.html('<br/>')

    # Logout
    utils.log_out()