import streamlit as st
from loguru import logger
from generate_app.z_apps.interfaces.s2_qualification_w import IncidentFormInterfaceStep2

if 'data' not in st.session_state:
    st.write("No data in session state")
    st.stop()
else:
    type_incident = st.session_state.data.incident_type
st.header("🎯 Gestion des Incidents - Qualification")
interfaces = IncidentFormInterfaceStep2(type_incident)
interfaces.show_form()
st.write("---")
interfaces.table_view()
