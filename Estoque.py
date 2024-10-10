import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import plotly.express as px
from src import utils

# Page config
st.set_page_config(page_title="Treevia LC", layout="wide")

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
st.sidebar.image(name_path)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Authentication
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(clear_on_submit=True)

# Bars
def make_client_bar():
    n_client = (estq_data_filter
        .groupby(['cliente'])
        .size()
        .to_frame("size")
        .reset_index()
        .sort_values('size'))
    
    n_client['percent'] = n_client['size']/n_client['size'].sum()
    fig = px.bar(n_client, x='size', y='cliente', labels={'size': 'N° de Sensores', 'cliente': 'Cliente'}, )
    fig.update_layout(margin=dict(t=10, b=10), height=300)

    return fig

# Pie
def make_status_pie():
    n_status = (estq_data
        .groupby(['status'])
        .size()
        .to_frame("size")
        .reset_index()
        .sort_values('size'))
    
    fig = px.pie(n_status, values='size', names='status')
    fig.update_layout(margin=dict(t=10, b=10, l=50, r=5), height=250)
    return fig

# API Calls
estq = utils.call_estoque()
devc = utils.call_device()
exch = utils.call_exchange()

# Exchange data
exch_data = pd.DataFrame(exch.json()['result'])
exch_data['date'] = pd.to_datetime(exch_data['exch_ts_unix_timestamp'], unit='ms')

# Device data
devc_data = pd.DataFrame(devc.json()['result'])
devc_data = devc_data[['id', 'devc_cd_macaddress_treevia']]

# Inventory data
estq_data = pd.DataFrame(estq.json())
estq_data = estq_data.astype(str)
estq_data['data'] = pd.to_datetime(estq_data['data'])
estq_data['cliente'] = utils.translate_clients(estq_data['cliente'])
clients = list(utils.translate_clients(estq_data['cliente']).unique())

# Gauges
estq_size = estq_data.shape[0]
estq_val = estq_data.loc[estq_data['status'] == 'Estoque Treevia'].shape[0]
prob_val = estq_data.loc[estq_data['status'].str.startswith('P')].shape[0]
client_val = estq_data.loc[estq_data['status'] == 'Enviado para cliente'].shape[0]

# Layout
if st.session_state['authentication_status']:
    with st.sidebar:
        options = st.multiselect("Cliente(s)", clients)

    estq_data_filter = estq_data if len(options) == 0 else estq_data.loc[estq_data['cliente'].isin(options)]
    col1, col2, col3= st.columns((.20, .40, .40), gap="small")
    
    with col1:
        st.metric("Sensores em Estoque", estq_val, help="Número de sensores disponíveis para envio para clientes.")
        st.metric("Sensores problemáticos", prob_val, help="Número de sensores com qualquer status de categoria \"P\".")
        st.metric("Sensores com clientes", client_val, help="Número de sensores na possesão de cliente.")
    
    with col2:
        st.plotly_chart(make_client_bar(), use_container_width=True)
    
    with col3:
        st.plotly_chart(make_status_pie(), use_container_width=True)   
    
    st.dataframe(exch_data, height=300, use_container_width=True)    
    
    authenticator.logout(location='sidebar')

elif st.session_state['authentication_status'] is False:
    st.toast('Usuário/Senha inválidos.')

elif st.session_state['authentication_status'] is None:
    st.toast('Insira Usuário e Senha.')