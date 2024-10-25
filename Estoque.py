import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import plotly.express as px
from src import utils
from datetime import datetime

# Page config
st.set_page_config(page_title="Treevia LC", layout="wide")

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
st.sidebar.image(name_path, use_column_width=True)

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

# Bar plot
def make_client_bar(x):
    n_client = (x
        .groupby(['cliente', 'devc_is_refurbished'])
        .size()
        .to_frame("size")
        .reset_index())
    
    n_client['percent'] = n_client['size']/n_client['size'].sum()
    fig = px.bar(
        n_client, 
        x='size',
        y='cliente', 
        color ='devc_is_refurbished',
        labels={'size': 'N° de Sensores', 'cliente': 'Cliente', 'devc_is_refurbished': 'Remanufaturado?'})
    fig.update_layout(margin=dict(t=10, b=10), height=250)

    return fig

# Pie plot
def make_status_pie(x):
    n_status = (x
        .groupby(['status'])
        .size()
        .to_frame("size")
        .reset_index()
        .sort_values('size'))
    
    fig = px.pie(n_status, values='size', names='status')
    fig.update_layout(margin=dict(t=20, b=20, l=50, r=5), height=300)
    return fig

# Layout
if "lorem" in st.query_params:

    # Date filter
    with st.sidebar:
        data_inicial = st.date_input(label="Data Inicial", value=datetime(2023, 1, 1))
        data_final = st.date_input(label="Data Final", value='today')

    # API Calls
    estq = utils.call_estoque()
    devc = utils.call_device()

    # Device data
    devc_data = pd.DataFrame(devc.json()['result'])
    devc_data = devc_data[['id', 'devc_cd_macaddress_treevia', 'devc_is_refurbished']]

    # Inventory data
    estq_data = pd.DataFrame(estq.json())
    estq_data = estq_data.astype(str)
    estq_data['data'] = pd.to_datetime(estq_data['data']).dt.date
    estq_data['cliente'] = utils.translate_clients(estq_data['cliente'])
    estq_data = estq_data.merge(devc_data, left_on='mac', right_on='devc_cd_macaddress_treevia')
    estq_data = estq_data.loc[(estq_data['data'] >= data_inicial) & (estq_data['data'] <= data_final)]
    clients = list(utils.translate_clients(estq_data['cliente']).unique())

    # Gauges
    estq_size = estq_data.shape[0]
    estq_val = estq_data.loc[estq_data['status'] == 'Estoque Treevia'].shape[0]
    prob_val = estq_data.loc[estq_data['status'].str.startswith('P')].shape[0]
    client_val = estq_data.loc[estq_data['status'] == 'Enviado para cliente'].shape[0]

    # Row 1
    col1, col2, col3 = st.columns((.20, .40, .40), gap="small")

    with col1:
        st.metric("Sensores em Estoque", estq_val, help="Número de sensores disponíveis para envio para clientes.")
        st.metric("Sensores problemáticos", prob_val, help="Número de sensores com qualquer status de categoria \"P\".")
        st.metric("Sensores com clientes", client_val, help="Número de sensores na possesão de cliente.")
    with col2:
        options = st.multiselect("Cliente(s)", clients)
        estq_data_filter = estq_data if len(options) == 0 else estq_data.loc[estq_data['cliente'].isin(options)]
        st.plotly_chart(make_client_bar(estq_data_filter), use_container_width=True) 
    with col3:
        st.plotly_chart(make_status_pie(estq_data), use_container_width=True)   
    
    # Row 2
    col_names = {'cliente':'Cliente', 'status': 'Status', 'mac': 'MAC', 'data': 'Data', 'devc_is_refurbished':'Remanufaturado?'}
    st.dataframe(estq_data[['cliente', 'status', 'mac', 'data', 'devc_is_refurbished']].rename(columns=col_names), height=280, use_container_width=True, hide_index=True)
else:
    st.toast("Not authorized.")