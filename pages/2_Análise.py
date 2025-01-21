import streamlit as st
import pandas as pd
from src import utils
from st_supabase_connection import SupabaseConnection, execute_query
import pathlib

# Configuração da página
st.set_page_config(page_title="Treevia LC - Análise", layout='wide', page_icon='assets/favicon.ico')

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
css_path = pathlib.Path(__file__).parents[1] / "assets" / "tl_styles.css"
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
    rows = execute_query(conn.table("timeline").select("*"), ttl="5m")
    time_data = pd.DataFrame(rows.data)
    time_data['data'] = pd.to_datetime(time_data['data'])
    max_date = time_data['data'].dt.date.max()
    min_date = time_data['data'].dt.date.min()

    # Renderizando filtros
    with st.sidebar:
        flt_macs = st.text_area('MACs').splitlines()
        flt_date = st.slider('Data de Cadastro', min_value=min_date, max_value=max_date, format='DD/MM/YYYY', value=(min_date, max_date))

    # Aplicando filtros
    time_data = utils.filter_timeline(time_data, flt_macs, flt_date)
    
    # Calculando n° de ciclos e tempo para falha
    fail_per_cycle = utils.fail_time(time_data)
    agg_data = utils.avg_fail_time(time_data)
    avg_num_cycles = round(agg_data['num_ciclos'].mean(), 2)
    try: avg_fail_time = int(agg_data['tempo_medio_falha'].mean()) 
    except: avg_fail_time = 0

    # Criando plots
    time_bars = utils.time_bar_plot(time_data, 'status')
    scatter_plot = utils.cycle_scatterplot(fail_per_cycle)
    cycle_bars = utils.cycle_barplot(time_data)

    # Renderizando plots e tabelas
    cols1 = st.columns((.2, .4, .4))
    with cols1[0]:
        st.metric('Nº Médio de Ciclos', avg_num_cycles)
        st.metric('Tempo Médio de Falha', str(avg_fail_time) + ' dias')
    with cols1[1]:
        st.plotly_chart(time_bars, use_container_width=True)
    with cols1[2]:
        st.plotly_chart(scatter_plot, use_container_width=True)
    cols2 = st.columns((.35, .25, .4))
    with cols2[0]:
        st.markdown('**N° de Ciclos x Tempo Médio para Falha**')
        st.dataframe(agg_data, use_container_width=True, hide_index=True, height=300)
    with cols2[1]:
        st.markdown('**Ciclo x Tempo de Vida**')
        st.dataframe(fail_per_cycle, use_container_width=True, hide_index=True, height=300)
    with cols2[2]:
        st.markdown('**N° de Sensores Acumulado por Ciclo**')
        st.plotly_chart(cycle_bars)
    cols3 = st.columns(1)
    with cols3[0]:
        st.markdown('**Registros de Timeline**')
        st.dataframe(time_data, use_container_width=True, hide_index=True)
    st.html('<br/>')

    # Logout
    utils.log_out()

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    st.switch_page('Home.py')
