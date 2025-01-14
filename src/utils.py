import streamlit as st
import requests as rqs
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
from st_supabase_connection import SupabaseConnection, execute_query

@st.cache_data(show_spinner="Carregando Estoque...")
def call_estoque():
    estq = rqs.get(st.secrets["estoque_url"])
    return estq

@st.cache_data(show_spinner="Carregando Devices...")
def call_device():
    devc = rqs.get(st.secrets["device_url"])
    return devc

@st.cache_data(show_spinner="Carregando Hardwares...")
def call_hw():
    hw = rqs.get(st.secrets["hardware_url"])
    return hw

@st.cache_data(show_spinner="Carregando Trocas...")
def call_exchange():
    exch = rqs.get(st.secrets["exchange_url"])
    return exch

def filter_timeline(df, macs=None, dates=None):

    if macs is not None and len(macs) >= 1:
        df = df[df['macs'].isin(macs)]

    if dates is not None:
        df = df[df['data'].dt.date.between(dates[0], dates[1])]  

    return df

def filter_home(df, clientes, status, dates):

    if status is not None and len(status) >= 1:
        df = df[df['status'].isin(status)]

    if clientes is not None and len(clientes) >= 1:
        df = df[df['cliente'].isin(clientes)]

    if dates is not None:
        df = df[df['data'].dt.date.between(dates[0], dates[1])]

    return df

def update_db(data, conn, db):
    response = execute_query(
        conn.table(db).insert(data), ttl=0
    )

    st.toast(body=response)

def upsert_db(data, conn, db):
    response = execute_query(
        conn.table(db).upsert(data, on_conflict=['macs'])
    )

    st.toast(body=response)

def update_sensores(data, conn):
    upsert_db(data, conn, 'estoque')
    update_db(data, conn, 'timeline')

def format_bool(x):
    res = 'Sim' if x == True else 'Não'
    return res

def pie_plotly(data, name, value, title, height):
    pie = go.Figure(data=[go.Pie(
            labels=data[name], 
            values=data[value],
            showlegend=False,
            hole=.3)]) 
    
    pie.update_layout( 
        height=height,
        margin=dict(t=25, b=0, l=0, r=0),
        title=dict(text=title),
        paper_bgcolor='rgba(0,0,0,0)')
    
    return pie

def get_batch(df, match_column, match_value, target_column, date_column):
    try:
        filter_df = df[df[match_column] == match_value]
        sort_df = filter_df.sort_values(by=date_column, ascending=True)
        last_value = sort_df[target_column].iloc[-1]
        return last_value
    except:
        return None
    
def get_cycle(df, match_column, match_value, target_column, date_column, increase=0):
    try:
        filter_df = df[df[match_column] == match_value]
        sort_df = filter_df.sort_values(by=date_column, ascending=True)
        last_values = sort_df[target_column].iloc[-1]
        return last_values + increase
    except:
        return 1

def convert_date(x):
    return datetime.strptime(x, '%Y-%m-%d').date()

def custom_mean(x):
    if len(x) > 1:
        res = np.sum(x)/(len(x)-1)
    else:
        res = None
    return res

def avg_fail_time(df):
    agg_data = (
        df
            .groupby(['macs', 'ciclo'])
            .apply(delta_time, include_groups=False)
            .reset_index(name='fail_time')
            .groupby('macs')
            .agg({'fail_time': [len, custom_mean]})
    )

    agg_data.columns = agg_data.columns.droplevel()
    agg_data.reset_index(inplace=True)
    agg_data = agg_data.rename(columns={'len': 'num_ciclos', 'custom_mean': 'tempo_medio_falha'})

    return agg_data

def time_bar_plot(df, var):
    bar_data = (
        df
        .groupby([var, 'data'])
        .size()
        .reset_index(name='counts')
        .sort_values(by='data')
    )  
    bar_data['data'] = bar_data['data'].dt.strftime('%Y-%m-%d')
    fig = px.bar(bar_data, x='data', y='counts', orientation='v', color=var, barmode='relative')
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        height=200, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0))
    return fig

def log_out():
        with st.sidebar:
            sb_cols = st.columns(3)
            with sb_cols[1]:
                st.session_state['authenticator'].logout()

delta_time = lambda group: int((group['data'].max() - group['data'].min()).days)

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

problemas = [
    'Quarentena',
    'Bateria',
    'Mecânica',
    'Não limpa memória',
    'Não conecta na Jiga',
    'Timeout',
    'Não atualiza',
    'Não faz dump'
]