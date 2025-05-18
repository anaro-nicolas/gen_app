import streamlit as st
from loguru import logger
from generate_app.z_apps.interfaces.s1_new_w import IncidentFormInterfaceStep1


st.header("🎯 Gestion des Incidents - Création")
    
interfaces = IncidentFormInterfaceStep1()
interfaces.show()
