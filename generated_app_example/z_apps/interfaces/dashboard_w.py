import streamlit as st
from loguru import logger
from generate_app.z_apps.specific.bl_incident import BLIncident

class DashboardInterface:
    def __init__(self):
        self.bl_incident = BLIncident()
        if st.session_state.user.user_id:
            self.user_id = st.session_state.user.user_id
            logger.debug(f"User ID: {self.user_id}")
        else :
            self.user_id = 1
        self.filter=f"created_by=={self.user_id}"

    def show_data(self):
        logger.debug("Getting incidents data")
        df = self.bl_incident.get_incidents_and_qualifications_by_filter(self.filter)
        return df
        
    def get_stats(self)->tuple[int,int,int,int,int]:
        logger.debug("Getting stats")
        try:
            total = self.bl_incident.get_nb_incidents_total()
            my_incidents = self.bl_incident.get_nb_incidents_total_user(self.user_id)
            create = self.bl_incident.get_nb_incidents_created()
            qualification = self.bl_incident.get_nb_incidents_in_qulify() + self.bl_incident.get_nb_incidents_in_prioritize()
            resolve = self.bl_incident.get_nb_incidents_in_resolve()
        except Exception as e:
            logger.error(f"Error while getting stats: {e}")
            logger.exception("TRACEBACK")
            total,create,qualification,resolve,my_incidents = 0,0,0,0,0
        
        return create,qualification,resolve,total,my_incidents
