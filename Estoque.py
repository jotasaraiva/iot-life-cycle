import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src import utils

st.set_page_config(page_title="Treevia LC", layout="wide")

# API Calls
estq = utils.call_estoque()

# Inventory data
estq_data = pd.DataFrame(estq.json())
estq_data = estq_data.astype(str)
estq_data['data'] = pd.to_datetime(estq_data['data'])

# Gauges
estq_size = estq_data.shape[0]
estq_val = estq_data.loc[estq_data['status'] == 'Estoque Treevia'].shape[0]
prob_val = estq_data.loc[estq_data['status'].str.startswith('P')].shape[0]

# Bars

def make_client_bar():
    n_client = (estq_data
        .groupby(['cliente'])
        .size()
        .to_frame("size")
        .reset_index()
        .sort_values('size'))
    
    n_client['percent'] = n_client['size']/n_client['size'].sum()
    n_client['cliente'] = utils.translate_clients(n_client['cliente'])
    fig = px.bar(n_client, x='size', y='cliente', labels={'size': 'N° de Sensores', 'cliente': 'Cliente'})
    fig.update_layout(paper_bgcolor='whitesmoke', height=350, margin=dict(t=20, b=20))

    return fig

n_status = (estq_data
    .groupby(['status'])
    .size()
    .to_frame("size")
    .reset_index()
    .sort_values('size'))

# n_status['percent'] = n_status['size']/n_status['size'].sum()

#fig = px.bar(n_status, x='size', y='status', labels={'size': 'N° de Sensores', 'status': ''})
#cols[0].plotly_chart(fig)
#fig = px.bar(n_client, x='size', y='cliente', labels={'size': 'N° de Sensores', 'cliente': ''})
#cols[1].plotly_chart(fig)

col1, col2, col3= st.columns((.25, .5, .25), gap="small")

with col1:
    st.metric("Sensores em Estoque", estq_val)
    st.metric("Sensores problemáticos", prob_val)

with col2:
    st.plotly_chart(make_client_bar())