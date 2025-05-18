import streamlit as st
from loguru import logger
from generate_app.z_apps.interfaces.s3_priorize_w import IncidentFormInterfaceStep3

st.header("🎯 Gestion des Incidents - Track resolution")

interfaces = IncidentFormInterfaceStep3()
interfaces.show_form()
st.write("---")
interfaces.table_view()