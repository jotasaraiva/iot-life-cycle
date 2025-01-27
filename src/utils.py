import streamlit as st
import requests as rqs
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
from st_supabase_connection import SupabaseConnection, execute_query

# Funções para resgatar dados da API Device (não usadas)
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

# Filtrar dados da timeline
def filter_timeline(df, macs=None, dates=None):

    if macs is not None and len(macs) >= 1:
        df = df[df['macs'].isin(macs)]

    if dates is not None:
        df = df[df['data'].dt.date.between(dates[0], dates[1])]  

    return df

# Filtrar dados de estoque
def filter_home(df, clientes, status, dates):

    if status is not None and len(status) >= 1:
        df = df[df['status'].isin(status)]

    if clientes is not None and len(clientes) >= 1:
        df = df[df['cliente'].isin(clientes)]

    if dates is not None:
        df = df[df['data'].dt.date.between(dates[0], dates[1])]

    return df

# Fazer update no banco
def update_db(data, conn, db):
    response = execute_query(
        conn.table(db).insert(data), ttl=0
    )

    st.toast(body=response)

# Fazer upsert no banco
def upsert_db(data, conn, db):
    response = execute_query(
        conn.table(db).upsert(data, on_conflict=['macs'])
    )

    st.toast(body=response)

# Fazer as duas operações anteriores em uma só função
def update_sensores(data, conn):
    upsert_db(data, conn, 'estoque')
    update_db(data, conn, 'timeline')

# Formatar dados booleanos para Sim e Não
def format_bool(x):
    res = 'Sim' if x == True else 'Não'
    return res

# Fazer plot rosca
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

# Resgatar dados de lotes
def get_batch(df, match_column, match_value, target_column, date_column):
    try:
        filter_df = df[df[match_column] == match_value]
        sort_df = filter_df.sort_values(by=date_column, ascending=True)
        last_value = sort_df[target_column].iloc[-1]
        return last_value
    except:
        return None
    
# Resgatar dados de ciclo
def get_cycle(df, match_column, match_value, target_column, date_column, increase=0):
    try:
        filter_df = df[df[match_column] == match_value]
        sort_df = filter_df.sort_values(by=date_column, ascending=True)
        last_values = sort_df[target_column].iloc[-1]
        return last_values + increase
    except:
        return 1

# Converter data
def convert_date(x):
    return datetime.strptime(x, '%Y-%m-%d').date()

# Média condicional (se tiver apenas um valor, retorna None
# se tiver mais de um valor, o cálculo é soma(x)/(len(x)-1)
def custom_mean(x):
    if len(x) > 1:
        res = np.sum(x)/(len(x)-1)
    else:
        res = None
    return res

# Calcular tempo para falha
def fail_time(df):
    fail_per_cycle = (
        df
            .groupby(['macs', 'ciclo'])
            .apply(delta_time, include_groups=False)
            .reset_index(name='fail_time')
    )

    return fail_per_cycle

# Calcular tempo médio até a falha
def avg_fail_time(df):
    fail_per_cycle = fail_time(df)
    agg_data = (
        fail_per_cycle
            .groupby('macs')
            .agg({'fail_time': [len, custom_mean]})
    )

    agg_data.columns = agg_data.columns.droplevel()
    agg_data.reset_index(inplace=True)
    agg_data = agg_data.rename(columns={'len': 'num_ciclos', 'custom_mean': 'tempo_medio_falha'})

    return agg_data

# Plot de barra da timeline
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

# Scatterplot de ciclo x tempo para falha
def cycle_scatterplot(df):
    fig = px.scatter(df, x='ciclo', y='fail_time', hover_data=['macs'])
    fig.update_layout(
        height=200, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0))
    return fig

# Plot de barra de contagem de sensores em cada ciclo
def cycle_barplot(df):
    bar_data = (
        df
        .groupby('ciclo')
        .size()
        .reset_index(name='counts')
    )

    fig = fig = px.bar(bar_data, x='ciclo', y='counts', orientation='v')
    fig.update_layout(
        height=300, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0))

    return fig

# Botão de logout
def log_out():
        with st.sidebar:
            sb_cols = st.columns(3)
            with sb_cols[0]:
                pass
            with sb_cols[2]:
                pass
            with sb_cols[1]:
                st.session_state['authenticator'].logout('Sair')

# Calcular diferença entre data máxima e mínima
delta_time = lambda group: int((group['data'].max() - group['data'].min()).days)

# Variáveis globais
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
    'Bateria',
    'Mecânica',
    'Não limpa memória',
    'Não conecta na Jiga',
    'Não atualiza',
    'Não faz dump'
]