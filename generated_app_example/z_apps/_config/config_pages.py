import streamlit as st
from loguru import logger
from generate_app.z_apps.interfaces.authentication_w import AuthenticationInterface
authentication = AuthenticationInterface()

## pages defined bt functions
def logout():
    authentication.logout()
    
##Account
dashboard = st.Page(
    "Account/dashboard.py", 
    title="Dashboard", 
    icon=":material/dashboard:",
)
settings = st.Page(
    "Account/settings.py", 
    title="Settings", 
    icon=":material/settings:",
) 
logout_page = st.Page(
    logout, 
    title="Log out", 
    icon=":material/logout:"
)

## Incidents
new = st.Page(
    "Incidents/s1_new.py",
    title="New Incident",
    icon=":material/help:",
)
classify = st.Page(
    "Incidents/s2_classify.py", 
    title="Classify Incident", 
    icon=":material/bug_report:",
)
priority = st.Page(
    "Incidents/s3_priorization.py", 
    title="Given priotity", 
    icon=":material/bug_report:",
)
resolve = st.Page(
    "Incidents/s4_resolve.py", 
    title="Resolve & close", 
    icon=":material/bug_report:",
)
report = st.Page(
    "Incidents/s5_report.py", 
    title="Reporting & Archive", 
    icon=":material/bug_report:",
)

## Admin
a_forrms=st.Page(
    "Admin/forms.py", 
    title="Configure forms for application", 
    icon=":material/bug_report:",
)
a_users=st.Page(
    "Admin/users.py", 
    title="Manage application users", 
    icon=":material/bug_report:",
)
a_refrences=st.Page(
    "Admin/references.py", 
    title="Modify references", 
    icon=":material/bug_report:",
)

## Navigation model
account_pages = [dashboard, settings, logout_page ]
incident_pages = [new, classify, priority, resolve, report]
admin_pages = [a_forrms, a_users, a_refrences]



    
