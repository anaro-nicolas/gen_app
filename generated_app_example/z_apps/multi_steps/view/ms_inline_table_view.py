from typing import Dict, List, Optional, Any
import streamlit as st
from loguru import logger
from generate_app.z_apps.multi_steps.base.ms_json_utils import MSJsonUtils
from generate_app.z_apps.specific.bl_incident import BLIncident
# Ajout de l'import pour le helper qui gère les listes
from generate_app.z_apps.multi_steps.base.ms_helper import MSHelper

class InlineTableView:
    """Vue tableau avec édition inline, sans dépendance au workflow"""
    
    def __init__(self, config_path: str, table_name: str):
        self.config_path = config_path
        self.table_name = table_name
        self.ms_json = MSJsonUtils(config_path)
        self.bl_incident = BLIncident()
        # Initialiser le helper pour gérer les listes déroulantes
        self.ms_helper = MSHelper()
        # Propriété pour fixer la largeur de la colonne des actions (modifiable)
        self.action_col_width: float = 1.8  
        # État local pour l'édition
        if 'inline_edit_state' not in st.session_state:
            st.session_state.inline_edit_state = {
                'editing': {},  # {table_name: record_id}
                'new_record': {}  # {table_name: bool}
            }
    
    def load_configuration(self) -> Dict:
        """Charge la configuration de la table"""
        try:
            data = self.ms_json.extract_sub_dict_from_json(False, self.table_name)
            if not data:
                raise ValueError(f"Configuration non trouvée pour {self.table_name}")
            return data
        except Exception as e:
            logger.error(f"Erreur de chargement de configuration: {e}")
            raise

    def render(self) -> None:
        """Affiche le tableau avec édition inline"""
        try:
            # Injection de CSS pour forcer l'affichage inline des boutons
            st.markdown("""
            <style>
              div.stButton > button {
                  display: inline-block;
                  margin-right: 5px;
              }
            </style>
            """, unsafe_allow_html=True)

            config = self.load_configuration()
            table_config = config.get('tableMaster', {})
            fields_config = config.get('fields', {})

            if not table_config or not fields_config:
                st.error("Configuration invalide")
                return

            self._buttons_security_key = config.get("form-buttons", {}).get("security-key", self.table_name)

            # Utilisation de self.action_col_width pour la dernière colonne
            header_cols = st.columns([3] * len(fields_config) + [self.action_col_width])
            for i, (field_name, field_config) in enumerate(fields_config.items()):
                with header_cols[i]:
                    st.markdown(f"**{field_config.get('label', field_name)}**")
            with header_cols[-1]:
                st.markdown("**Actions**")
            st.markdown("---")  # Séparateur

            # Affichage des données
            records = self._load_records(table_config['table'])
            for record in records:
                self._render_record_row(record, fields_config)

        except Exception as e:
            logger.error(f"Erreur d'affichage: {e}")
            st.error("Une erreur est survenue")

    def _render_new_record_form(self, fields_config: Dict) -> None:
        """Affiche le formulaire de création"""
        with st.container(border=True):
            st.write("Nouveau")
            form_cols = st.columns([3] * len(fields_config) + [1])
            form_data = {}
            for i, (field_name, field_config) in enumerate(fields_config.items()):
                with form_cols[i]:
                    form_data[field_name] = self._render_field_input(field_name, field_config, None, is_new=True)
            # Affiche les boutons dans la dernière cellule (sans imbriquer de colonnes supplémentaires)
            with form_cols[-1]:
                if st.button("✔️", key=f"{self._buttons_security_key}_create_save"):
                    self._save_new_record(form_data)
                if st.button("❌", key=f"{self._buttons_security_key}_create_cancel"):
                    st.session_state.inline_edit_state['new_record'][self.table_name] = False
                    st.rerun()

    def _render_record_row(self, record: Dict, fields_config: Dict) -> None:
        """Affiche une ligne du tableau avec les boutons d'action alignés horizontalement."""
        is_editing = st.session_state.inline_edit_state['editing'].get(self.table_name) == record['id']
        # Création d'une grille avec une colonne par champ et 2 colonnes à la fin pour les boutons
        num_fields = len(fields_config)
        # Pour fixer la largeur des boutons, on divise self.action_col_width en deux sous-colonnes
        if is_editing:
            cols = st.columns([3] * num_fields + [self.action_col_width/2, self.action_col_width/2])
        else:
            cols = st.columns([3] * num_fields + [self.action_col_width/2, self.action_col_width/2])
            
        form_data = {}
        
        # Affichage des valeurs (ou des inputs en mode édition) pour chaque champ
        idx = 0
        for field_name, field_config in fields_config.items():
            with cols[idx]:
                if is_editing:
                    form_data[field_name] = self._render_field_input(
                        field_name, field_config, record.get(field_name))
                else:
                    display_value = self._get_display_value(field_config, record.get(field_name))
                    st.write(display_value)
            idx += 1
        
        # Affichage des boutons sans ajouter un niveau de nesting
        if is_editing:
            with cols[-2]:
                if st.button("✔️", key=f"{self._buttons_security_key}_save_{record['id']}"):
                    self._update_record(record['id'], form_data)
            with cols[-1]:
                if st.button("❌", key=f"{self._buttons_security_key}_cancel_{record['id']}"):
                    st.session_state.inline_edit_state['editing'][self.table_name] = None
                    st.rerun()
        else:
            with cols[-2]:
                if st.button("✏️", key=f"{self._buttons_security_key}_edit_{record['id']}"):
                    st.session_state.inline_edit_state['editing'][self.table_name] = record['id']
                    st.rerun()
            with cols[-1]:
                if st.button("🗑️", key=f"{self._buttons_security_key}_delete_{record['id']}"):
                    self._delete_record(record['id'])

    def _render_field_input(self, field_name: str, field_config: Dict, value: Any, is_new: bool = False) -> Any:
        """Affiche un champ de formulaire selon son type"""
        form_type = field_config.get('form', {}).get('type', 'text')
        key_suffix = 'new' if is_new else str(value)
        
        if form_type == 'select':
            # Gestion des listes déroulantes en mode édition (inspiré de ms_form_view / ms_table_view)
            form_dict = field_config.get('form', {})
            source_type = form_dict.get('source_type')
            key = f"{field_name}_{key_suffix}"
            if source_type == 'sgbd':
                source = form_dict.get('source')
                field_view = form_dict.get('field-view', 'name')
                field_record = form_dict.get('field-record', 'id')
                where_clause = form_dict.get("where", {})
                options_dict = self.ms_helper.fetch_sgbd_options(source, field_view, field_record, where_clause)
                options = list(options_dict.keys())
                index = 0
                if value:
                    for opt in options:
                        if str(options_dict.get(opt)) == str(value):
                            index = options.index(opt)
                            break
                return st.selectbox(
                    label=" ",
                    options=options,
                    index=index,
                    key=key,
                    label_visibility="collapsed"
                )
            else:
                # Pour les cas "enum" ou autres
                options = self._get_select_options(field_config)
                index = 0
                if value and value in options:
                    index = options.index(value)
                return st.selectbox(
                    label=" ",
                    options=options,
                    index=index,
                    key=key,
                    label_visibility="collapsed"
                )
        elif form_type == 'textarea':
            return st.text_area(
                label=" ",
                value=value or "",
                key=f"{field_name}_{key_suffix}",
                label_visibility="collapsed"
            )
        elif form_type == 'number':
            return st.number_input(
                label=" ",
                value=float(value) if value else 0,
                key=f"{field_name}_{key_suffix}",
                label_visibility="collapsed"
            )
        else:  # text par défaut
            return st.text_input(
                label=" ",
                value=value or "",
                key=f"{field_name}_{key_suffix}",
                label_visibility="collapsed"
            )

    def _get_select_options(self, field_config: Dict) -> List:
        """Récupère les options pour un champ select en s'appuyant sur MSHelper"""
        source_type = field_config.get('form', {}).get('source_type')
        source = field_config.get('form', {}).get('source')
        
        if source_type == 'enum' and isinstance(source, list):
            return source
        elif source_type == 'sgbd':
            # Utiliser MSHelper pour récupérer un dictionnaire d'options
            field_view = field_config.get('form', {}).get('field-view', 'name')
            field_record = field_config.get('form', {}).get('field-record', 'id')
            options_dict = self.ms_helper.fetch_sgbd_options(source, field_view, field_record, {})
            logger.debug(f"Options trouvées pour {field_config.get('label')}: {options_dict}")
            return list(options_dict.keys())
        return []

    def _get_display_value(self, field_config: Dict, value: Any) -> str:
        """Obtient la valeur d'affichage pour un champ"""
        if field_config.get('form', {}).get('type') == 'select':
            source = field_config.get('form', {}).get('source')
            if isinstance(source, str):  # sgbd
                model_class = self.bl_incident.db.get_class_model(source)
                if model_class:
                    try:
                        record = model_class.get_by_id(value)
                        return str(getattr(record, field_config.get('form', {}).get('field-view', 'name')))
                    except:
                        pass
        return str(value) if value is not None else ""

    def _load_records(self, table_name: str) -> List[Dict]:
        """Charge les enregistrements de la table"""
        try:
            model_class = self.bl_incident.db.get_class_model(table_name)
            if not model_class:
                return []
                
            records = model_class.select().dicts()
            return list(records)
        except Exception as e:
            logger.error(f"Erreur de chargement des données: {e}")
            return []

    def _save_new_record(self, data: Dict) -> None:
        """Sauvegarde un nouvel enregistrement"""
        try:
            config = self.load_configuration()
            table_name = config['tableMaster']['table']
            
            success = self.bl_incident.create_reference_item(table_name, data)
            if success:
                st.success("Enregistrement créé avec succès")
                st.session_state.inline_edit_state['new_record'][self.table_name] = False
                st.rerun()
            else:
                st.error("Erreur lors de la création")
        except Exception as e:
            logger.error(f"Erreur de sauvegarde: {e}")
            st.error("Erreur lors de la sauvegarde")

    def _update_record(self, record_id: int, data: Dict) -> None:
        """Met à jour un enregistrement en utilisant directement le connecteur de base de données"""
        try:
            config = self.load_configuration()
            table_name = config['tableMaster']['table']
            ModelClass = self.bl_incident.db.get_class_model(table_name)
            success = self.bl_incident.db.update_record(ModelClass, record_id, **data)
            if success:
                st.success("Mise à jour réussie")
                st.session_state.inline_edit_state['editing'][self.table_name] = None
                st.rerun()
            else:
                st.error("Erreur lors de la mise à jour")
        except Exception as e:
            logger.error(f"Erreur de mise à jour: {e}")
            st.error("Erreur lors de la mise à jour")

    def _delete_record(self, record_id: int) -> None:
        """Supprime un enregistrement"""
        try:
            config = self.load_configuration()
            table_name = config['tableMaster']['table']
            
            success = self.bl_incident.delete_reference_item(table_name, record_id)
            if success:
                st.success("Suppression réussie")
                st.rerun()
            else:
                st.error("Erreur lors de la suppression")
        except Exception as e:
            logger.error(f"Erreur de suppression: {e}")
            st.error("Erreur lors de la suppression")