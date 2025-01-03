import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
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
css_path = pathlib.Path(__file__).parents[0] / "assets" / "styles.css"
load_css(css_path)

# Layout
if st.session_state['authentication_status']:

    conn = st.connection("supabase", type=SupabaseConnection)
    rows = execute_query(conn.table("estoque").select("*"), ttl="5m")
    estq_data = pd.DataFrame(rows.data)
    cols = st.columns((.4, .3, .3))
    
    with cols[0]:
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric(
                'Sensores em Estoque', 
                estq_data.groupby(['status']).size()['Estoque'],
                border=True
            )
            st.metric(
                'Sensores saudáveis',
                len(estq_data.loc[(estq_data['defeito'] == False) & (estq_data['status'] == 'Estoque')]),
                border=True
            )
            st.metric(
                'Sensores defeituosos',
                len(estq_data.loc[(estq_data['defeito'] == True) & (estq_data['status'] == 'Estoque')]),
                border=True
            )
        with metric_cols[1]:
            st.metric(
                'Sensores em Remanufatura',
                len(estq_data.loc[estq_data['status'] == 'Remanufatura']),
                border=True
            )
            st.metric(
                'Sensores em Cliente',
                len(estq_data.loc[estq_data['status'] == 'Cliente']),
                border=True
            )
            st.metric(
                'Sensores totais',
                len(estq_data),
                border=True
            )

    with cols[2]:
        pie_data = estq_data.groupby(['status']).size().reset_index(name='counts')
        fig = px.pie(pie_data, values='counts', names='status', hole=.5)
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig)

    st.dataframe(estq_data, use_container_width=True, hide_index=True)

    authenticator.logout(location='sidebar')

elif st.session_state['authentication_status'] == False:
    st.toast('Username/password incorrect.')
elif st.session_state['authentication_status'] == None:
    st.toast('Enter user and password.')