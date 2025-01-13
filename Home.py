import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src import utils
from datetime import datetime
from st_supabase_connection import SupabaseConnection, execute_query
import pathlib

# Page config
st.set_page_config(page_title="Treevia LC", layout="wide")

authenticator = stauth.Authenticate(
    st.secrets['credentials'].to_dict(),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)

authenticator.login()
st.session_state['authenticator'] = authenticator

# Logo
logo_path="assets/treevia-logo.png"
name_path="assets/treevia-name.png"
st.logo(logo_path)
st.sidebar.image(name_path, use_container_width=True)

# CSS config
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
css_path = pathlib.Path(__file__).parents[0] / "assets" / "home_styles.css"
load_css(css_path)

# Layout
if st.session_state['authentication_status']:

    conn = st.connection("supabase", type=SupabaseConnection)
    rows = execute_query(conn.table("estoque").select("*"), ttl="5m")
    estq_data = pd.DataFrame(rows.data)
    cols1 = st.columns((.2, .2, .2, .4))
    
    with cols1[0]:
        st.metric(
            'IoTs em Estoque', 
            len(estq_data[estq_data['status'] == 'Estoque'])
        )
        st.metric(
            'IoTs saudáveis',
            len(estq_data.loc[(estq_data['defeito'] == False) & (estq_data['status'] == 'Estoque')])
        )
        st.metric(
            'IoTs defeituosos',
            len(estq_data.loc[(estq_data['defeito'] == True) & (estq_data['status'] == 'Estoque')])
        )
    with cols1[1]:
        st.metric(
            'IoTs em Remanufatura',
            len(estq_data.loc[estq_data['status'] == 'Remanufatura'])
        )
        st.metric(
            'IoTs em Cliente',
            len(estq_data.loc[estq_data['status'] == 'Cliente'])
        )
        st.metric(
            'IoTs totais',
            len(estq_data)
        )
    with cols1[2]:
        status_pie_data = estq_data.groupby(['status']).size().reset_index(name='counts')
        status_pie = utils.pie_plotly(status_pie_data, 'status', 'counts', 'Status', 140)
        st.plotly_chart(status_pie, use_container_width=True)

        defeito_pie_data = estq_data.groupby(['defeito']).size().reset_index(name='counts')
        defeito_pie_data['defeito'] = defeito_pie_data['defeito'].replace({True: 'Defeituosos', False: 'Saudáveis'})
        defeito_pie = utils.pie_plotly(defeito_pie_data, 'defeito', 'counts', 'Defeituosos', 140)
        st.plotly_chart(defeito_pie, use_container_width=True)
    with cols1[3]:
        bars_data = estq_data.groupby(['cliente']).size().reset_index(name='counts')
        bars = px.bar(bars_data, x='counts', y='cliente', orientation='h')
        bars.update_layout(
            xaxis_title=None, 
            yaxis_title=None, 
            height=300, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(bars, use_container_width=True)

    st.dataframe(estq_data, height=210, hide_index=True, use_container_width=True)     

    utils.log_out()

elif st.session_state['authentication_status'] == False:
    st.toast('Username/password incorrect.')
elif st.session_state['authentication_status'] == None:
    st.toast('Enter user and password.')