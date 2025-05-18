import streamlit as st
from loguru import logger
from typing import Optional
from generate_app.z_apps.multi_steps.view.ms_inline_table_view import InlineTableView
from generate_app.z_apps.multi_steps.base.ms_json_utils import MSJsonUtils
from generate_app.z_apps.specific.bl_incident import BLIncident

class RefAdminW:
    """Interface d'administration des tables de référence"""
    
    def __init__(self):
        self.path_file = "generate_app/z_apps/middle_model/ref.json"
        self.bl_incident = BLIncident()
        self.ms_json = MSJsonUtils(self.path_file)
        self.ref_tables = {}
        
    def initialize_ref_table(self, table_name: str) -> Optional[InlineTableView]:
        """Initialise ou récupère une table de référence"""
        if table_name not in self.ref_tables:
            try:
                table_view = InlineTableView(self.path_file, table_name)
                self.ref_tables[table_name] = table_view
            except Exception as e:
                logger.error(f"Erreur d'initialisation de la table {table_name}: {e}")
                return None
        return self.ref_tables[table_name]

    def show_ref_table(self, table_name: str, container) -> None:
        """Affiche une table de référence"""
        try:
            # Récupérer le label de la table depuis la configuration
            config = self.ms_json.extract_sub_dict_from_json(False, table_name)
            label = config.get('tableMaster', {}).get('label', table_name)
            
            with container.expander(label):
                ref_table = self.initialize_ref_table(table_name)
                if ref_table:
                    ref_table.render()
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de {table_name}: {e}")
            st.error(f"Impossible d'afficher la table {table_name}")

    def show_ref_admin(self):
        """Affiche l'interface d'administration des références"""
        try:
            st.title("Administration des Tables de Référence")
            
            # Charger la configuration depuis le fichier JSON
            config = self.ms_json.load_json_file()
            
            # Organiser les tables par paires pour l'affichage
            tables = list(config.keys())
            pairs = [(tables[i], tables[i+1]) if i+1 < len(tables) else (tables[i], None) 
                     for i in range(0, len(tables), 2)]

            # Afficher les tables en colonnes
            for table1, table2 in pairs:
                col1, col2 = st.columns(2)
                self.show_ref_table(table1, col1)
                if table2:
                    self.show_ref_table(table2, col2)

        except Exception as e:
            logger.error(f"Erreur générale dans show_ref_admin: {e}")
            logger.exception("Traceback:")
            st.error("Une erreur est survenue lors de l'affichage des références")