import streamlit as st
from loguru import logger
import pandas as pd
from datetime import datetime
from generate_app.z_apps.multi_steps.view.ms_form_view import MSFormView
from generate_app.z_apps.multi_steps.view.ms_table_view import MSTableView

class IncidentFormInterfaceStep3:
    def __init__(self):
        self.master_id = st.session_state.data.incident_id
        self.master_type = st.session_state.data.incident_type
        self.master_step = st.session_state.data.step 
        self.color = st.session_state.data.color
        self.master_type_id = st.session_state.data.incident_type_id
        
        self.view_form = False
        if self.master_id and self.master_type:
            self.view_form = True
      
    def show_form(self):
        if 'data' in st.session_state:
            st.write(f"step: {self.master_step}, incident_id: {self.master_id}, incident_type: {self.master_type}, incident_type_id:{self.master_type_id} ,color : {self.color}")
        else:
            st.write("No data in session state")
        
        if not self.view_form:
            st.info("Please select an incident in the table below")
            st.page_link("Incidents/s2_qualification.py", "Qualufy Incident")
            
        else:
            st.subheader("Step3 : Complete the priorization")
            #détermine date de détection:
            
            # Création d'une instance de la vue de formulaire
            config_path = f"generate_app/z_apps/middle_model/{self.master_type}_v2.json"
            form_view = MSFormView(config_path, "Priorization")
            form_view.form_view()
    
    def table_view(self):
        # Création d'une instance de la vue de tableau
        config_path = f"generate_app/z_apps/middle_model/{self.master_type}_v2.json"
        table_view = MSTableView(config_path, "Priorization")
        #table_view = MultiStepTableView(config_path, "Qualify")
        table_view.table_view()