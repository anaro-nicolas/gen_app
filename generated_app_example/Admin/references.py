import streamlit as st
from generate_app.z_apps.interfaces.ref_admin_w import *

st.header("Admin : References Management")

ref_admin_interface = RefAdminW()
ref_admin_interface.show_ref_admin()
