import streamlit as st
from generate_app.z_apps._config.config_pages import *
from generate_app.z_apps.interfaces.authentication_w import User
st.set_page_config(layout="wide")

def home():
    #st.title="# 🎯 Incident Monitoring Tool"
    
    with st.expander(
        label="🔒 Connexion", 
        expanded=False
    ): 
        authentication.login()
        
    st.title("Gestionnaire d'Incidents")
    
    st.header("🏠 Notre Mission")
   
    st.write("""
    Notre application de gestion des incidents vous accompagne dans le suivi et la résolution 
    des problèmes de qualité. Elle permet une approche structurée en 5 étapes pour garantir 
    une résolution efficace et une capitalisation des connaissances.
    """)
    
    st.subheader("🔑 Fonctionnalités Principales")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        #### 📅 Gestion des Incidents
        - Création et suivi des incidents
        - Qualification détaillée du problème
        - Priorisation basée sur la gravité
        - Suivi des actions correctives
        - Génération de rapports
        """)
        
    with col2:
        st.write("""
        #### 🛠️ Outils d'Analyse
        - Tableaux de bord interactifs
        - Matrices de priorité
        - Historique des résolutions
        - Base de connaissances
        - Export des données
        """)
    st.write("---")
      
    st.subheader("📈 Process en 5 Étapes")
    st.write("""
    1. **Création** - Identification et enregistrement initial
    2. **Qualification** - Analyse détaillée et contextualisation
    3. **Priorisation** - Évaluation de l'impact et de l'urgence
    4. **Résolution** - Suivi des actions correctives
    5. **Capitalisation** - Documentation et partage des apprentissages
    """)
    
    st.info("""
    💡 **Pour commencer**, connectez-vous avec vos identifiants d'entreprise.
    L'accès aux fonctionnalités est personnalisé selon votre profil utilisateur.
    """)

def run():
    
    if 'user' not in st.session_state:
        st.session_state.user = User()
    
    role = st.session_state.user.role
    #config page
    st.title("Incident Monitoring Tool")

    page_dict = {}
    if role == "USER":
        page_dict["Account"] = account_pages
        page_dict["Incident"] = incident_pages
    if role == "ADMIN":
        page_dict["Account"] = account_pages
        page_dict["Incident"] = incident_pages
        page_dict["Admin"] = admin_pages

    ### Restriction by role
    if role == "USER" or role == "ADMIN":
        # user connected
        try:   
            dashboard._default = True
            pg = st.navigation(page_dict)
            pg.run()
        except Exception as e:
            logger.error(f"Error loading page: {e}")
            logger.exception("TRACEBACK")
            st.error("Error loading page: {e}")
    else:
        #login_page._default = True
        pg = st.navigation([st.Page(home)])
        #pg = login_page
        pg.run()
        
if __name__ == "__main__":
    run()