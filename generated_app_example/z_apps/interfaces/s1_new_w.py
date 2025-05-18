import streamlit as st
from loguru import logger
from datetime import datetime
from generate_app.z_apps.specific.bl_incident import BLIncident, Stepping
from generate_app.z_apps._config.config_pages import classify
import pandas as pd



class IncidentFormInterfaceStep1:
    def __init__(self):
        self.bl_incident = BLIncident()
        if "user_id" not in st.session_state:
            st.session_state.user.user_id = 1
        self.user_id = st.session_state.user.user_id

    def set_step2_incident_id(self, incident_id:int, incident_type_id:int, incident_type:str, color:str):
        st.session_state.data = Stepping()
        st.session_state.data.incident_id = incident_id
        st.session_state.data.incident_type = incident_type[:3].lower()
        st.session_state.data.incident_type_id = incident_type_id
        st.session_state.data.code = incident_type
        st.session_state.data.color=color
        st.session_state.data.step = 2
    
    def table_values_v2(self, step):
        incidents_step1 = self.bl_incident.get_incidents_step1()
        logger.debug(f"Step1 incidents: {incidents_step1}")
        if len(incidents_step1) < 1:
            st.success("No incidents in creating state in database")
            return
        with st.container():
            cols = st.columns(4)
            with cols[0]: st.write("**Code**")
            with cols[1]: st.write("**Type**")
            with cols[2]: st.write("**Référence**")
            with cols[3]: st.write("**Step2 : Qualification**")
            st.divider
            btn_redirect = {}
            for incident in incidents_step1:
                color = incident['color']
                background_color = f"background-color: #{color};"
                text_color = "color: white;"  # Uniform text color"
                padding = "padding: 16px;"
                cols = st.columns(4)
                with cols[0]:    
                    st.markdown(f"<div style=' {background_color} {padding} {text_color}'>{incident['code']}</div>", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"<div style=' {padding} {text_color}'>{incident['type']}</div>", unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"<div style=' {padding} {text_color}'>{incident['ref']}</div>", unsafe_allow_html=True)
                with cols[3]:
                    st.markdown(f"<div style='padding: 0px;'>", unsafe_allow_html=True)
                    btn_redirect[f"btn_{incident['id']}"] = st.button("Qualify", key=f"Q_{incident['id']}", on_click=lambda id=incident['id'],type_id=incident['type_id'],type=incident['code'],color=color: self.set_step2_incident_id(id, type_id, type, color))
                    st.markdown("</div>", unsafe_allow_html=True)
                st.write("---")
            for key_btn, bnt_value in btn_redirect.items():
                if bnt_value:
                    st.switch_page(classify)
    
    def show(self):
        st.subheader("Step 1: Define the initial incident")
        type_selected=None
        incident_type=0
        col1, col2, col3 = st.columns(3)
        with col1:
            ref = st.text_input(label="Ref", label_visibility="collapsed",placeholder="Give a reference")
        with col2:
            list_options = self.bl_incident.get_options("incident_types")
            logger.info(f"Options: {list_options}")

            type_selected = st.selectbox(
                label="Type",
                options=list_options.keys(),
                key="s1-type",
                index=None,
                label_visibility="collapsed",
                placeholder="Choose a type"
            )
            if type_selected:
                incident_type = list_options[type_selected]
        with col3:
            add = st.button("add", key="s1-create")
        
        try:
            if add:
                ok = self.bl_incident.create_state1_incident(
                    type=incident_type,
                    ref=ref,
                    user_id=self.user_id
                )
                if ok:
                    st.success("Incident created")
                    st.rerun()
                else:
                    st.error("Error creating incident")
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            st.error(f"Error during this operation")
                
        
        self.table_values_v2("step1")
        
        
    