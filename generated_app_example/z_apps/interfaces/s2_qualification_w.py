import streamlit as st
from loguru import logger
import pandas as pd
from datetime import datetime
from generate_app.z_apps.multi_steps.view.ms_form_view import MSFormView
from generate_app.z_apps.multi_steps.view.ms_table_view import MSTableView

class IncidentFormInterfaceStep2:
    def __init__(self, type_incident: str = "cus"):
        self.view_form = False
        self.id_incident = None
        self.type_incident = type_incident
        self.incident_type_id = 0
        self.color = None
        if 'data' in st.session_state:
            self.view_form = st.session_state.data.step == 2 and st.session_state.data.incident_id != None
            if self.view_form:
                self.id_incident = st.session_state.data.incident_id
                self.incident_type_id = st.session_state.data.incident_type_id
                self.type_incident = st.session_state.data.incident_type
                self.color = f"#{st.session_state.data.color}"
      
    def show_form(self):
        if 'data' in st.session_state:
            st.write(f"step: {st.session_state.data.step}, incident_id: {self.id_incident}, incident_type: {self.type_incident}, incident_type_id:{self.incident_type_id} ,color : {self.color}")
        else:
            st.write("No data in session state")
        
        if not self.view_form:
            st.info("Please select an incident in the table below")
            
            st.page_link("Incidents/s1_new.py")
            
        else:
            st.subheader("Step2 : Complete the qualification")
            #détermine date de détection:
            
            # Création d'une instance de la vue de formulaire
            config_path = f"generate_app/z_apps/middle_model/{self.type_incident}_v2.json"
            form_view = MSFormView(config_path, "Qualify")
            form_view.form_view()
    
    def table_view(self):
        # Création d'une instance de la vue de tableau
        config_path = f"generate_app/z_apps/middle_model/{self.type_incident}_v2.json"
        table_view = MSTableView(config_path, "Qualify")
        #table_view = MultiStepTableView(config_path, "Qualify")
        table_view.table_view()