from loguru import logger
import streamlit as st
from generate_app.z_apps.specific.bl_incident import BLIncident
from generate_app.z_apps.specific.base_model import *
from generate_app.z_apps.common.db_conector3 import DBConnector3


class MSHelper:
    
    
    def __init__(self)->None:
        self.db_connector = DBConnector3()
        self.bl_incident = BLIncident()
    
    def fetch_options_from_database(self, table: str, field_view: str, field_record: str, where_clause: dict) -> dict:
        """
        Récupère les options depuis la BDD pour un champ select.
        Retourne un dictionnaire {id: valeur_affichage} pour Streamlit
        """
        try:
            ModelClass = self.db_connector.get_class_model(table)
            if not ModelClass:
                logger.error(f"Model introuvable pour la table '{table}'.")
                return {}

            query = ModelClass.select(getattr(ModelClass, field_view), getattr(ModelClass, field_record))
            if where_clause:
                for field, value in where_clause.items():
                    query = query.where(getattr(ModelClass, field) == value)

            # Construire un dictionnaire {id: valeur_affichage}
            options_dict = {}
            for record in query:
                display_val = getattr(record, field_view)
                record_val = getattr(record, field_record)
                options_dict[display_val] = record_val

            return options_dict

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des options: {e}")
            return {}
        
    def delete_master_record(self, table_name: str, record_id: int) -> bool:
        """Delete a master record and its related records"""
        try:
            ModelClass = self.bl_incident.db.get_class_model(table_name)
            success = self.bl_incident.db.delete_record(ModelClass, record_id)
            if success:
                st.success("Record deleted successfully!")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete master record: {e}")
            st.error("Failed to delete record")
            return False
        
    def get_display_value(self, source_config: dict, value: any) -> str:
        """Récupère la valeur d'affichage pour un champ select/sgbd"""
        try:
            if not source_config or not value:
                logger.error(f"Invalid source configuration or value : {source_config}, {value}")
                return "Note found SC ou V"
            #logger.warning(f"=========> source_config: {source_config}")
            table_name = source_config.get("source")
            field_view = source_config.get("field-view") or source_config.get("field_view") or "name"
            field_record = source_config.get("field-record") or source_config.get("field_record") or "id"

            # Récupérer le modèle
            ModelClass = self.bl_incident.db.get_class_model(table_name)
            if not ModelClass:
                return "Note found MC"

            # Requête pour trouver l'enregistrement
            record = (ModelClass
                     .select(getattr(ModelClass, field_view))
                     .where(getattr(ModelClass, field_record) == value)
                     .first())

            if record:
                return getattr(record, field_view)
            return "Note found RC"

        except Exception as e:
            logger.error(f"Error getting display value: {e}")
            #logger.exception("Traceback:")
            return "Note found ERR"
        
    def fetch_sgbd_options(self, table: str, field_view: str, field_record: str, where_clause: dict) -> dict:
   
        logger.info(f"Fetching SGBD options from {table}")

        ModelClass = self.bl_incident.db.get_class_model(table)
        #logger.debug(f"Model class: {ModelClass}")
        view=eval(f"{ModelClass.__name__}.{field_view}")
        records=eval(f"{ModelClass.__name__}.{field_record}")
        query = ModelClass.select(view, records)
        if where_clause is not None:
            for w_field, w_value in where_clause.items():
                query = query.where(getattr(ModelClass, w_field) == w_value)

        results = {}
        
        for row in query:
            display_val = getattr(row, field_view, None)
            record_val = getattr(row, field_record, None)
            if display_val is not None:
                results[display_val]=record_val
        return results
    
    def _build_master_table_query(self, ModelClass, fields_config: dict, where_conditions: dict):
        """Helper to build master table query with proper joins"""
        query = ModelClass.select()
        
        # Add joins for any select fields that reference other tables
        for field_name, field_config in fields_config.items():
            form_config = field_config.get("form", {})
            #logger.debug(f" ________________ Form name: {form_config}")
            if (form_config.get("type") == "select" and 
                form_config.get("source_type") == "sgbd"):
                source_config = form_config.get("source", {})
                if isinstance(source_config, str):
                    table_name = source_config
                    field_view = "name"
                    field_record = "id"
                else:
                    table_name = source_config.get("table")
                    field_view = source_config.get("field-view", "name")
                    field_record = source_config.get("field-record", "id")
                
                RefModel = self.bl_incident.db.get_class_model(table_name)
                if RefModel:
                    query = query.join(
                        RefModel,
                        on=(getattr(ModelClass, field_name) == getattr(RefModel, field_record)),
                        join_type=JOIN.LEFT_OUTER
                    )
                    query = query.select_extend(getattr(RefModel, field_view).alias(f"{field_name}_display"))

        # Apply where conditions
        for field, value in where_conditions.items():
            query = query.where(getattr(ModelClass, field) == value)
            
        return query
    
    def get_count_records(self,table_st:str=None,secondary_table_config:dict=None)->str:
        ModelClass = self.bl_incident.db.get_class_model(table_st)
        relation_field = secondary_table_config.get("relation", "")
        master_id = st.session_state.data.incident_id
        count = (ModelClass
                .select()
                .where(getattr(ModelClass, relation_field) == master_id)
                .count())
        record_count = f" ({count})"
        logger.debug(f"Record count: {record_count}")
        return record_count
    
    def add_secondary_record(self, table_name: str, relation_field: str, form_data: dict) -> bool:
        """
        Creates a new record in the secondary table. 
        Because adding more shit to track is what we do best! 🎯
        """
        logger.debug(f"Received form_data for secondary record: {form_data}")  # <-- Ajout
        try:
            ModelClass = self.bl_incident.db.get_class_model(table_name)
            
            # Add the relation field to form data
            form_data[relation_field] = st.session_state.data.incident_id
            
            logger.debug(f"Creating secondary record with data: {form_data}")
            record_id = self.bl_incident.db.create_record(ModelClass, **form_data)
            logger.debug(f"Created record_id: {record_id}")  # <-- Ajout
            
            if record_id:
                st.success("Record added successfully! 🎉")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to add secondary record: {e}")
            logger.exception("Traceback:")
            st.error("Failed to add record 💩")
            return False

    def update_secondary_record(self, table_name: str, record_id: int, form_data: dict) -> bool:
        """
        Updates an existing record in the secondary table.
        Time to update this bad boy! 🔧
        """
        try:
            ModelClass = self.bl_incident.db.get_class_model(table_name)
            success = self.bl_incident.db.update_record(ModelClass, record_id=record_id, **form_data)
            
            if success:
                st.success("Record updated successfully! 🎉")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update secondary record: {e}")
            #logger.exception("Traceback:")
            st.error("Failed to update record 💩")
            return False

    def delete_secondary_record(self, table_name: str, record_id: int) -> bool:
        """
        Deletes a record from the secondary table.
        Say goodbye to this record! 👋
        """
        try:
            ModelClass = self.bl_incident.db.get_class_model(table_name)
            success = self.bl_incident.db.delete_record(ModelClass, record_id)
            
            if success:
                st.success("Record deleted successfully! 🗑️")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete secondary record: {e}")
            #logger.exception("Traceback:")
