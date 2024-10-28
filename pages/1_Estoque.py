import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from src import utils
import datetime

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

# Global vars
clientes = [
    "ELKS Engenharia Florestal e Ambiental Ltda",
    "BRF",
    "Bracell São Paulo",
    "WorldTree",
    "Suzano Inventário",
    "SLB",
    "CLIENTE TREINAMENTO",
    "Treevia Consultoria",
    "Klabin",
    "Saint-Gobain",
    "Melhoramentos Florestal",
    "Agencia Florestal Ltda",
    "CMPC",
    "Bracell Bahia Florestal",
    "Marques_Pro",
    "Simasul Siderurgia",
    "Desafio Cabruca",
    "Placas do Brasil S.A",
    "UNESP",
    "TRC",
    "Projeto UFT",
    "High Precision",
    "Gaia Agroflorestal",
    "QA - Ambiente de Testes",
    "Treevia Forest Technologies",
    "Corus Agroflorestal",
    "Teste Veracel",
    "Forte Florestal",
    "Veracel",
    "Radix",
    "demo_treevia",
    "Grupo Mutum",
    "Treevia - Equipe de Quality Analyst",
    "Bracell",
    "Remasa",
    "G2 Forest",
    "Inventec",
    "KLINGELE PAPER NOVA CAMPINA LTDA",
    "R.S FLORESTAL LTDA",
    "Trial 2a Rotação",
    "NORFLOR EMPREENDIMENTOS AGRÍCOLAS S/A",
    "GELF SIDERURGIA S/A",
    "ALJIBES AZULES S.A",
    "Trail",
    "SFDEMO2",
    "PARCEL REFLORESTADORA LDTA",
    "TTG Brasil Investimentos Florestais Ltda.",
    "Suzano Papel e Celulose",
    "Smart Forest Demo 2",
    "High Precision Demo",
    "3A Composites",
    "Laminados AB",
    "Projeto NANORAD'S",
    "Floresta Assesoria e Planejamento Florestal LTDA",
    "Farol Consultoria Agroflorestal",
    "Madeireira Rio Claro",
    "LIF - Land Inovation Fund",
    "Taboão Reflorestamento SA",
    "Colpar Participações",
    "Agrobusiness Floresta e Pecuária",
    "Cenibra",
    "Unesp - Acadêmico",
    "Google_PlayStore",
    "Topo_Floresta",
    "MANTENA FLORESTAL S.A.",
    "FoxFlorestal",
    "Treevia - Equipe de Desenvolvimento",
    "Vallourec",
    "Eldorado Brasil Celulose S/A",
    "Eldorado Máxima Produtividade",
    "Atenil S.A.",
    "Teste Front 2.0 - Apagar EAGG",
    "Test_Front 2.0",
    "Treevia - Equipe de Data Analisys",
    "Norflor Prognose Apresentacao",
    "Thalis",
    "Smart Forest Demo",
    "Aldeir Testes Corporation",
    "Brafor Projetos Ambientais Ltda",
    " Eldorado Inventario Tradicional",
    "Minasligas",
    "PONTUAL BIOENERGIA LTDA",
    "Teste IFQ",
    "The Nature Conservancy",
    "Treevia Academy"
]

# Check authentication state
if 'authenticator' not in st.session_state:
    st.switch_page('Dashboard.py')
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Dashboard.py')
    
# Layout
if st.session_state['authentication_status']:

    # API Calls
    devc = utils.call_device()

    # Data
    devc_data = pd.DataFrame(devc.json()['result'])[['id','devc_cd_macaddress_treevia']]
    estq_data = pd.read_csv("data/estoque.csv")

    if 'show_form' not in st.session_state:
        st.session_state['show_form'] = True

    # Logout
    st.session_state['authenticator'].logout(location='sidebar')

    # Layout  
    with st.popover('Cadastro de Estoque'):
        macs = st.text_area('MACs')
        status = st.selectbox('Status', ('Estoque', 'Cliente', 'Remanufatura'), index=None)
        lote_receb = None
        lote_treevia = None
        if status == 'Cliente':
            cliente = st.selectbox('Cliente', tuple(clientes))
            origem = None
        elif status == 'Estoque':
            origem = st.selectbox('Origem', ('Fornecedor', 'Cliente'))
            cliente = None
            if origem == 'Fornecedor':
                lote_receb = st.text_input('Lote de Recebimento')
                lote_treevia = st.text_input('Lote Interno')
        else:
            cliente = None
            origem = None
        if origem == 'Fornecedor':
            new_data = pd.DataFrame({
                'macs': macs.splitlines(),
                'status': status,
                'cliente': cliente,
                'origem': origem,
                'lote_recebimento': lote_receb,
                'lote_treevia': lote_treevia,
                'data': datetime.datetime.today().date()
            })
        else:
            new_data = pd.DataFrame({
                'macs': macs.splitlines(),
                'status': status,
                'cliente': cliente,
                'origem': origem,
                'data': datetime.datetime.today().date()
            })
        if new_data.shape[0] != 0:
            st.markdown('Preview')
            st.dataframe(new_data, use_container_width=True, hide_index=True)
        st.button('Subir', on_click=utils.update_or_add_rows, args=['data/estoque.csv', 'macs', new_data],use_container_width=True, type='primary')
    st.markdown('**Estoque cadastrado**')
    st.dataframe(estq_data, use_container_width=True, hide_index=True, height=550)