import streamlit as st
from generate_app.z_apps.interfaces.json_wizard import JSONWizard

def show_forms():
    st.header("Admin : Forms Management")
    wizard = JSONWizard("generate_app/z_apps/middle_model")
    
    st.markdown("## Visualisation des fichiers JSON")
    wizard.view_json_files()
    
    st.markdown("## Interface d'ajout d'un champ")
    wizard.add_field_interface()

show_forms()
