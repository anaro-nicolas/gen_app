import json
import datetime
import copy
from loguru import logger
import pandas as pd
import streamlit as st
from peewee import *
from typing import Optional
from generate_app.z_apps.multi_steps.base.ms_json_utils import *
from generate_app.z_apps.multi_steps.base.ms_helper import *
from generate_app.z_apps.specific.bl_incident import BLIncident
from generate_app.z_apps.specific.base_model import *

class MultiStepBase:
    """
    Holy crap, this is the main class for handling dynamic forms.
    It's a fucking mess but it works... most of the time.
    """
    
    def __init__(self, file_path: str, requires_workflow: bool = True):
        self.file_path: str = file_path
        self.status: Optional[str] = None
        self.cache: dict = {}
        self.bl_incident: BLIncident = BLIncident()
        self.fields_per_row = 4  # Number of fields per row in form
        # storage for form data
        self._form_data = {}
        self.requires_workflow = requires_workflow
        if self.requires_workflow and 'data' not in st.session_state:
            logger.error("Workflow data required but not found in session state")
            st.error("Session state error")
            return
        
        self.ms_json = MSJsonUtils(self.file_path)
        self.ms_helper = MSHelper()
        logger.info(f"MultiStepForm initialized with file: {file_path}")

    def set_status(self, status: str) -> None:
        """Sets the current form status."""
        self.status = status
        logger.info(f"Status updated to: {status}")
        
    def set_form_field(self, field_name: str, value: dict) -> None:
        """Store form values in this shitty internal cache"""
        self._form_data[field_name] = value 
        #logger.debug(f"Form field updated: {field_name}")

    
    @property    
    def get_status(self) -> Optional[str]:
        """Retrieves the current form status."""
        return self.status

    @property
    def get_form_field(self) -> dict:
        """Récupère les valeurs du formulaire"""
        return self._form_data

    ########################################################
    # Base Table private methods
    ########################################################
    
    def _create_table_columns(self, fields_config: dict) -> list:
        """
        Creates table columns configuration from fields JSON.
        Because tables need headers too! 
        """
        columns = []
        for field_name, field_config in fields_config.items():
            columns.append({
                "name": field_name,
                "label": field_config.get("label", field_name),
                "type": field_config.get("form", {}).get("type", "text")
            })
        return columns

    def _get_display_columns(self, fields_config: dict) -> list:
        """
        Extract display columns configuration from fields
        Returns list of tuples (field_name, label, width)
        """
        columns = []
        for field_name, field_conf in fields_config.items():
            # Skip hidden fields
            if field_conf.get("form", {}).get("type") == "hidden":
                continue
            # Determine column width based on field type
            width = 3  # default width
            if field_conf.get("form", {}).get("type") in ["textarea", "file"]:
                width = 4
            elif field_conf.get("form", {}).get("type") == "actions":
                width = 2
            columns.append((field_name, field_conf.get("label", field_name), width))
        return columns

    def _display_master_record(self, record: pd.Series, step_data: dict):
        """Helper to display a master record and its actions"""
        cols = st.columns([6, 2, 2])
        
        # Display record info
        with cols[0]:
            st.markdown(f"### {record.iloc[0]}")  # Affiche la première colonne comme titre
            
            # Affiche les autres colonnes sous forme de liste
            for col in record.index[1:]:
                st.write(f"**{col}:** {record[col]}")
                
        # Display action buttons
        with cols[1]:
            if "next_step" in step_data:
                if st.button("➡️ Next Step", key=f"next_{record.name}"):
                    self._handle_next_step(step_data["next_step"], record)
                    
        # Display secondary table expander if configured
        with cols[2]:
            secondary_config = step_data.get("tableSecondaire")
            if secondary_config:
                count = self.ms_helper.get_count_records(
                    secondary_config["table"],
                    secondary_config
                )
                with st.expander(f"({count}) Records"):
                    self._handle_secondary_table_view(
                        secondary_config,
                        master_id=record["id"]
                    )

    def _handle_next_step(self):
        """Updates session state based on next_step configuration"""
        logger.info("Handling next step...")
        st.session_state.data.step += 1

    #######################################################
    #  Base Form private methods
    #######################################################
    
    def make_form_object(self,field_info: dict,field_name:str) -> None:
        form={}
        #logger.debug(f"Field info: {field_info}")
        
        forms_items = field_info.get("form", {})
        #logger.debug(f"Form items: {forms_items}")
        
        value_obj = None
        
        field_type = field_info.get("form", {}).get("type", "unknown")
        #logger.debug(f"Field type: {field_type}")
        
        key_obj=field_info.get("security_key", field_name)
        label_obj=field_info.get("label", "not-defined")
        
        readonly_obj=forms_items.get("readonly", False)
        source=forms_items.get("source", None)
        source_type=forms_items.get("source_type", None)
        where_items=forms_items.get("where", None)
        view_id=forms_items.get("view_id", False)
        #logger.debug(f"Individual value: clés: {key_obj}, Label: {label_obj}, Readonly: {readonly_obj}, source: {source}, source_type: {source_type}, where_items: {where_items}")
        match field_type:      
            case "text":
                if source is not None and source_type is not None:
                    value_obj=self.get_value_from_source(source_type, source, where_items)
                
                if value_obj != "" and value_obj is not None:
                    form[key_obj] = st.text_input(
                        label=label_obj, 
                        key=key_obj, 
                        value=str(value_obj), # Convert to string
                        disabled=readonly_obj, 
                        label_visibility="visible",
                        placeholder=f"{label_obj} :{str(value_obj)}" # Convert to string
                    )
                else:
                    form[key_obj] = st.text_input(
                        label=label_obj, 
                        key=key_obj, 
                        disabled=readonly_obj,
                        label_visibility="collapsed", 
                        placeholder=label_obj
                    )
                value = st.session_state.get(key_obj)
                if value is not None:
                    self.set_form_field(field_name, {
                        "value": value,
                        "field_type": field_type
                    })

            case "textarea":
                text_content = ""
                if source and source_type:
                    text_content = self.get_value_from_source(source_type, source, where_items)

                form[key_obj] = st.text_area(
                    label=label_obj,
                    key=key_obj,
                    value=text_content or "",
                    disabled=readonly_obj,
                    label_visibility="collapsed",
                    placeholder=label_obj
                )
                value = st.session_state.get(key_obj)
                if value is not None:
                    self.set_form_field(field_name, {
                        "value": value,
                        "field_type": field_type
                    })

            case "boolean":
                st.write("Boolean placeholder comming soon")
            case "number":
                if source is not None and source_type is not None:
                    value_obj = int(self.get_value_from_source(source_type, source, where_items))
                initial_val = float(value_obj) if (value_obj and str(value_obj).isdigit()) else 0.0
                form[key_obj] = st.number_input(
                    label=label_obj,
                    key=key_obj,
                    value=initial_val,
                    disabled=readonly_obj,
                    label_visibility="collapsed",
                    placeholder=label_obj
                )
                value = st.session_state.get(key_obj)
                if value is not None:
                    self.set_form_field(field_name, {
                        "value": value,
                        "field_type": field_type
                    })

            case "date":
                if source is not None and source_type is not None:
                    value_obj = self.get_value_from_source(source_type, source, where_items)
                parsed_date = pd.to_datetime(value_obj) if value_obj else pd.to_datetime("today")
                form[key_obj] = st.date_input(
                    label=label_obj,
                    key=key_obj,
                    value=parsed_date,
                    disabled=readonly_obj,
                    label_visibility="collapsed"
                )
                value = st.session_state.get(key_obj)
                if value is not None:
                    self.set_form_field(field_name, {
                        "value": value,
                        "field_type": field_type
                    })
            case "file":
                destination_folder = forms_items.get("destination_folder", "uploads")
                base_url = forms_items.get("base_url", "")
                allowed_file_types = forms_items.get("type_files", ["pdf", "jpg", "png"])
                
                form[key_obj] = st.file_uploader(
                    label=label_obj,
                    key=key_obj,
                    type=allowed_file_types,
                    label_visibility="collapsed"
                )
                
            case "select":
                source_type = forms_items.get("source_type")
                logger.debug(f"Creating select field: {field_name} with source_type: {source_type}")

                # Get the current value if it exists in the form data
                current_data = self._form_data.get(field_name, {})
                current_value = current_data.get("value")
                logger.debug(f"Current value for {field_name}: {current_value}")

                if source_type == "sgbd":
                    try:
                        source = forms_items.get("source", {})
                        field_view = forms_items.get("field_view", "name")
                        field_record = forms_items.get("field_record", "id")
                        where_items = forms_items.get("where", {})
                        index_items = forms_items.get("index", -1)
            
                        # Get options from database
                        select_options = self.ms_helper.fetch_sgbd_options(
                            source,
                            field_view,
                            field_record, 
                            where_items
                        )
                        
                        if not select_options:
                            logger.warning(f"No options found for {field_name} from table {source}")
                            options = ["No data available"]
                            index = 0
                        else:
                            options = list(select_options.keys())
                            # Try to find the index of current value
                            if index_items != -1:
                                index = index_items
                            else:
                                if current_value is not None:
                                # Find the display value for the current ID
                                    display_value = next(
                                        (key for key, val in select_options.items() 
                                        if str(val) == str(current_value)), 
                                        None
                                    )
                                    index = options.index(display_value) if display_value in options else 0
                                else:    
                                    index = 0                            
                            
                    except Exception as e:
                        logger.error(f"Failed to load select options: {str(e)}")
                        #logger.exception("Traceback:")
                        options = ["Error loading data"]
                        index = 0
                        
                elif source_type == "enum":
                    options = forms_items.get("source", [])
                    if not options:
                        logger.warning(f"Empty enum options for field {field_name}")
                        options = ["No options defined"]
                        index = 0
                    else:
                        # For enum, try to find current value directly in options
                        index = options.index(current_value) if current_value in options else 0
                else:
                    logger.error(f"Unknown source type '{source_type}' for select field {field_name}")
                    options = ["Invalid configuration"]
                    index = 0
                if view_id:
                    col1, col2 = st.columns([0.75, 0.25])
                    with col1:
                        chosen_value = st.selectbox(
                            label=label_obj,
                            options=options,
                            index=index,
                            key=key_obj,
                            label_visibility="collapsed",
                            placeholder=label_obj
                        )
                else:
                    chosen_value = st.selectbox(
                        label=label_obj,
                        options=options,
                        index=index,
                        key=key_obj,
                        label_visibility="collapsed",
                        placeholder=label_obj
                    )
                # Store the selected value
                if chosen_value and chosen_value not in ["No data available", "Error loading data", "No options defined", "Invalid configuration"]:
                    if source_type == "sgbd":
                        selected_id = select_options.get(chosen_value)
                        if view_id:
                            with col2:
                                st.text_input(
                                    label="id",
                                    value=str(selected_id),
                                    key=f"{key_obj}_id",
                                    label_visibility="collapsed"
                                )
                        self.set_form_field(field_name, {
                            "value": selected_id,
                            "field_type": field_type
                        })
                    else:
                        self.set_form_field(field_name, {
                            "value": chosen_value,
                            "field_type": field_type  
                        })

                logger.debug(f"Select field {field_name} created with value: {chosen_value}")

            case "auto":
                logger.debug(f"Auto field type: {source_type}")
                data = self.get_value_from_source(source_type, source, where_items)
                logger.debug(f"Auto data: {data}")
                with st.container(border=True, height=44,key=key_obj):
                    st.write(data)
            case "hidden":
                logger.info(f"Hidden field label: {label_obj}")
            case _:
                st.write("Unknown field type, what the hell is this?")
    
    
    #######################################################
    # Common methods for form and table
    #######################################################
    
    def get_value_from_source(self, source_type:str, source:str=None, where_items:dict=None)->str:
        if source_type is  None :
            logger.warning(f"Source type is not defined: {source_type}")
            return ""
        match(source_type):
            case 'single':
                return source
            case 'enum':
                if isinstance(source, list) and len(source) > 0:
                    return source
                else:
                    logger.warning("Enum source is empty.")
                    return ""
            case 'session_var':
                try:
                    #source_session = st.empty()
                    source_session = eval(f"st.session_state.{source}")
                    if not source_session:
                        logger.warning("Source is None or empty")
                        return ""
                    logger.debug(f"Source session: {source_session}")
                    return str(source_session)
                except Exception as e:
                    logger.error(f"Error evaluating session variable: {e}")
                    return ""
            case "sgbd":
                table_name=source.get("table", "")
                field_view=source.get("field-view", "")
                field_record=source.get("field-record", "")
                where_clause=source.get("where", {})
                options=self.ms_helper.fetch_sgbd_options(table_name, field_view, field_record, where_clause)
                if where_items is not None:
                    selected_value=where_items.get(field_view, "")
                    return self.get_selected_id(options, selected_value)
                return ""
            case _:
                logger.warning(f"Unknown source type : {source_type}.")
                return ""
        
    
        
    
    
    def _create_horizontal_fields(self, fields_list: list, record: dict = None, is_new: bool = False) -> None:
        """
        Creates a horizontal layout for form fields.
        Because vertical forms are so 2020! 🎨
        """
        num_fields = len(fields_list)
        cols = st.columns(self.fields_per_row)
        
        for idx, (field_name, field_config) in enumerate(fields_list):
            col_idx = idx % self.fields_per_row
            with cols[col_idx]:
                if is_new:
                    new_config = field_config.copy()
                    new_config["security_key"] = f"new_{field_config['security_key']}"
                    self.make_form_object(new_config, field_name)
                else:
                    field_key = f"{field_config['security_key']}_{record['id']}"
                    mod_config = self._make_complete_form(field_config, record.get(field_name, ""))
                    
                    self.make_form_object({
                        **mod_config,
                        "security_key": field_key,
                        "form": {
                            **mod_config["form"]
                        }
                    }, field_name)

    def _make_complete_form(self, field_config: dict=None, value:any=None ) -> dict:
        form_type=field_config.get("form", {}).get("type", "unknown")
        if form_type not in ["file", "auto", "select","password"]:
            field_config["form"]["source_type"] = "single"
            field_config["form"]["source"] = value
        elif form_type == "select":
            field_config["form"]["selected_val"] = value
        elif form_type == "file":
            field_config["form"]["source"] = value
        return field_config
        
    def show_secondary_table(self, secondary_config: dict) -> None:
        try:
            # Get table config
            table_name = secondary_config.get("table", "")
            relation_field = secondary_config.get("relation", "")
            fields_config = secondary_config.get("fields", {})

            if not all([table_name, relation_field, fields_config]):
                logger.error("Missing required secondary table configuration")
                return

            ModelClass = self.bl_incident.db.get_class_model(table_name)
            ## AHHHHHH - TO DO: that change with the generic!!!!!!!!!!!!!!!!!!!!!!!!!!
            master_id = st.session_state.data.incident_id

            # Initialize session state for form visibility
            form_key = f"show_form_{table_name}"
            if form_key not in st.session_state:
                st.session_state[form_key] = False
            
            # Add button to show/hide form
            if st.button("➕ Add New Record", key=f"btn_toggle_{table_name}"):
                st.session_state[form_key] = not st.session_state[form_key]
            
            # Show form only when toggled
            if st.session_state[form_key]:
                with st.container(border=True):
                    # Create horizontal form fields
                    display_fields = [(k, v) for k, v in fields_config.items() if k != relation_field]
                    self._create_horizontal_fields(display_fields, is_new=True)
                    
                    # Action buttons
                    col1, col2 = st.columns([1, 11])
                    with col1:
                        if st.button("💾", key=f"save_new_{table_name}"):
                            add_form = {}
                            for field_name, field_config in fields_config.items():
                                if field_name == relation_field:
                                    continue
                                key = f"new_{field_config['security_key']}"
                                if key in st.session_state:
                                    add_form[field_name] = st.session_state[key]
                            if self.ms_helper.add_secondary_record(table_name, relation_field, add_form):
                                st.session_state[form_key] = False
                                st.rerun()
                    with col2:
                        if st.button("❌", key=f"cancel_new_{table_name}"):
                            st.session_state[form_key] = False
                            st.rerun()

            # Get and display existing records
            query = (ModelClass
                    .select()
                    .where(getattr(ModelClass, relation_field) == master_id))
            
            records = list(query.dicts())
            if records:
                #logger.debug(f"Found {len(records)} records in {table_name} and existing records: {records}")
                st.markdown("### Existing Records")
                
            for record in records:
                with st.container(border=True):
                    # Create horizontal fields for existing record
                    display_fields = [(k, v) for k, v in fields_config.items() if k != relation_field]
                    
                    self._create_horizontal_fields(display_fields, record)
                    
                    # Action buttons
                    col1, col2 = st.columns([1, 11])
                    with col1:
                        col3, col4 = st.columns(2)
                        with col3:
                            if st.button("💾", key=f"save_{table_name}_{record['id']}"):
                                update_form = {}
                                for field_name, field_config in fields_config.items():
                                    key = f"{field_config['security_key']}_{record['id']}"
                                    if key in st.session_state:
                                        update_form[field_name] = st.session_state[key]
                                self.ms_helper.update_secondary_record(table_name, record['id'], update_form)
                        with col4:
                            if st.button("🗑️", key=f"delete_{table_name}_{record['id']}"):
                                self.ms_helper.delete_secondary_record(table_name, record['id'])
                                st.rerun()

        except Exception as e:
            logger.error(f"Failed to show secondary table: {str(e)}")
            logger.exception("Traceback:")

    
    
    
   
    def _handle_secondary_table_view(self, secondary_config: dict, master_id: int) -> None:
        """
        Handles the display of secondary table data in an expander.
        """
        
        try:
            table_name = secondary_config.get("table", "")
            relation_field = secondary_config.get("relation", "")
            fields_config = secondary_config.get("fields", {})
            
            if not all([table_name, relation_field, fields_config]):
                logger.error("Missing required secondary table configuration")
                return

            ModelClass = self.bl_incident.db.get_class_model(table_name)
            
            # Get records with explicit field selection
            query = ModelClass.select().where(getattr(ModelClass, relation_field) == master_id)
            records = list(query.dicts())
            #logger.debug(f"Found {len(records)} records in {table_name}")
            if records:
                # Create DataFrame with configured fields only
                filtered_records = []
                for record in records:
                    filtered_record = {}
                    for field_name in fields_config.keys():
                        if field_name != relation_field:
                            filtered_record[field_name] = record.get(field_name)
                    filtered_records.append(filtered_record)
                
                df = pd.DataFrame(filtered_records)
                
                # Rename columns with labels
                display_cols = {
                    field_name: field_info.get("label", field_name)
                    for field_name, field_info in fields_config.items()
                    if field_name != relation_field
                }
                
                if not df.empty:
                    df = df.rename(columns=display_cols)
                    st.dataframe(df, hide_index=True, use_container_width=True)
                else:
                    st.info("No related records found")

        except Exception as e:
            logger.error(f"Failed to handle secondary table view: {str(e)}")
            #logger.exception("Traceback:")

    def _build_update_data(self, fields_config: dict, original_values: dict = None) -> dict:
        """
        Builds update data from form fields.
        Only includes fields that have actually changed from their original values.
        Because why update shit that hasn't changed? 
        """
        update_data = {}
        
        for field_name, field_info in fields_config.items():
            field_data = self._form_data.get(field_name)
            if not field_data:
                continue

            current_value = field_data.get("value")
            if current_value is None:
                continue

            # Si on a des valeurs originales, on ne garde que les champs modifiés
            if original_values and field_name in original_values:
                original_value = original_values.get(field_name)
                
                # Conversion en string pour comparer correctement
                str_current = str(current_value) if current_value is not None else None
                str_original = str(original_value) if original_value is not None else None
                
                if str_current != str_original:
                    logger.info(f"Field {field_name} changed: {str_original} -> {str_current}")
                    update_data[field_name] = current_value
            else:
                # Si pas de valeurs originales, on garde tout (cas des nouveaux enregistrements)
                update_data[field_name] = current_value

        if update_data:
            logger.info(f"Found {len(update_data)} modified fields")
            logger.debug(f"Modified fields: {list(update_data.keys())}")
        else:
            logger.info("No fields were modified")
            
        return update_data

    def _handle_form_submit(self, button_config: dict, table_master: str, status: str, label: str = None) -> None:
        logger.debug(f"Form submit called with table_master={table_master}, status={status}")  # <-- Ajout
        try:
            incident_id = st.session_state.data.incident_id
            if not incident_id:
                st.error("No incident ID found in session")
                return

            ModelClass = self.bl_incident.db.get_class_model(table_master)
            if not ModelClass:
                st.error(f"Invalid table: {table_master}")
                return
            # step not defined 
            step_data = self.ms_json.extract_sub_dict_from_json(False,self.get_status)
            if not step_data:
                st.error("Form configuration not found")
                return

            # Construire les données de mise à jour
            update_data = self._build_update_data(step_data.get("fields", {}))
            logger.debug(f"Update data: {update_data}")  # <-- Ajout
            
            # Ajouter le status courant
            update_data["status"] = self.get_status

            # Log pour validation
            #logger.warning(f"Updating record {incident_id} with data: {update_data}")
            
            # Mise à jour
            success = self.bl_incident.db.update_record(
                ModelClass,
                record_id=incident_id,
                **update_data
            )
            
            if success:
                st.success(f"Record successfully updated with status: {self.get_status}")
                st.rerun()
            else:
                st.error("Failed to update record")

        except Exception as e:
            logger.error(f"Failed to handle form submit: {e}")
            #logger.exception("Traceback:")
            st.error("Failed to process form submission")

    def _show_edit_form(self, fields_config: dict, record: dict) -> None:
        """Affiche le formulaire d'édition"""
        form_key_prefix = f"edit_{record['id']}_"
        
        # Stockage des valeurs originales si pas déjà fait
        if "original_values" not in st.session_state:
            st.session_state.original_values = {}
            
        if record["id"] not in st.session_state.original_values:
            st.session_state.original_values[record["id"]] = {}
        
        has_changes = False
        
        for field_name, field_info in fields_config.items():
            # Créer une copie profonde pour éviter de modifier l'objet d'origine
            
            field_config = copy.deepcopy(field_info)
            # Générer une clé unique en utilisant le préfixe et le nom de champ
            # Si la configuration possède une security_key, on y ajoute le préfixe, sinon on utilise le nom du champ
            base_key = field_config.get("security_key", field_name)
            field_key = f"{form_key_prefix}{base_key}"
            field_config["security_key"] = field_key
            
            # Précharger la valeur depuis le record
            if field_name in record:
                field_value = record[field_name]
                # Conversion en string si nécessaire
                if not isinstance(field_value, str):
                    field_value = str(field_value)
                    
                # Dans le cas d'un champ select, on va récupérer et ajuster l'index 
                if field_info.get("form", {}).get("type") == "select":
                    source_type = field_info.get("form", {}).get("source_type")
                    form_config = field_info.get("form", {})
                    
                    if source_type == "sgbd":
                        source = form_config.get("source")
                        select_options = self.ms_helper.fetch_sgbd_options(
                            source,
                            form_config.get("field_view", "name"),
                            form_config.get("field_record", "id"),
                            form_config.get("where", {})
                        )
                        
                        display_value = None
                        for key, val in select_options.items():
                            if str(val) == str(field_value):
                                display_value = key
                                break
                                
                        field_config["form"]["options"] = list(select_options.keys())
                        if display_value:
                            field_config["form"]["index"] = field_config["form"]["options"].index(display_value)
                        else:
                            field_config["form"]["index"] = 0
                    elif source_type == "enum":
                        options = form_config.get("source", [])
                        field_config["form"]["options"] = options
                        try:
                            field_config["form"]["index"] = options.index(field_value)
                        except ValueError:
                            field_config["form"]["index"] = 0
                else:
                    field_config["form"]["source"] = field_value
                    field_config["form"]["source_type"] = "single"
                
                # Stocker la valeur originale pour détecter les changements
                if field_key not in st.session_state.original_values[record["id"]]:
                    st.session_state.original_values[record["id"]][field_key] = str(field_value)
                
                # Vérifier si la valeur a changé
                if field_key in st.session_state:
                    current_value = str(st.session_state[field_key])
                    original_value = str(st.session_state.original_values[record["id"]][field_key])
                    if current_value != original_value:
                        has_changes = True
            
            # Appeler make_form_object avec cette configuration garantie unique
            self.make_form_object(field_config, field_name)
        
        # Afficher les boutons d'action
        col1, col2 = st.columns([1, 11])
        with col1:
            col3, col4 = st.columns(2)
            with col3:
                if not has_changes:
                    st.button("💾", key=f"{form_key_prefix}save", type="primary", disabled=True)
                else:
                    if st.button("💾", key=f"{form_key_prefix}save", type="primary", disabled=False):
                        self._handle_edit_save(fields_config, record)
            with col4:
                if st.button("❌", key=f"{form_key_prefix}cancel"):
                    if record["id"] in st.session_state.original_values:
                        del st.session_state.original_values[record["id"]]
                    st.session_state.editing_record = {
                        "id": None,
                        "is_editing": False,
                        "incident_type_id": st.session_state.data.incident_type_id
                    }
                    st.rerun()

    def _show_edit_form_old(self, fields_config: dict, record: dict) -> None:
        """Affiche le formulaire d'édition"""
        form_key_prefix = f"edit_{record['id']}_"
        
        # Stockage des valeurs originales si pas déjà fait
        if "original_values" not in st.session_state:
            st.session_state.original_values = {}
            
        if record["id"] not in st.session_state.original_values:
            st.session_state.original_values[record["id"]] = {}
        
        has_changes = False
        
        for field_name, field_info in fields_config.items():
            field_config = field_info.copy()
            field_key = f"{form_key_prefix}{field_config['security_key']}"
            field_config["security-key"] = field_key
            
            # Précharger la valeur depuis record
            if field_name in record:
                field_value = record[field_name]
                # Convertir en string si nécessaire
                if not isinstance(field_value, str):
                    field_value = str(field_value)
                    
                if field_info.get("form", {}).get("type") == "select":
                    # Pour les champs select...
                    source_type = field_info.get("form", {}).get("source_type")
                    form_config = field_info.get("form", {})
                    
                    if source_type == "sgbd":
                        # 1. Récupérer les options du select
                        source = form_config.get("source")
                        select_options = self.ms_helper.fetch_sgbd_options(
                            source,
                            form_config.get("field-view", "name"),
                            form_config.get("field-record", "id"),
                            form_config.get("where", {})
                        )
                        
                        # 2. Trouver la clé (field_view) correspondant à la valeur (field_record)
                        display_value = None
                        for key, val in select_options.items():
                            if str(val) == str(field_value):
                                display_value = key
                                break
                                
                        # 3. Préparer le select avec l'index correct
                        field_config["form"]["options"] = list(select_options.keys())
                        if display_value:
                            field_config["form"]["index"] = field_config["form"]["options"].index(display_value)
                            logger.debug(f"Préparation recherche index ::: Select field : {field_name} | value: {display_value} | index: {field_config['form']['index']}")
                        else:
                            field_config["form"]["index"] = 0
                            
                    elif source_type == "enum":
                        options = form_config.get("source", [])
                        field_config["form"]["options"] = options
                        try:
                            field_config["form"]["index"] = options.index(field_value)
                        except ValueError:
                            field_config["form"]["index"] = 0
                else:
                    field_config["form"]["source"] = field_value
                    field_config["form"]["source_type"] = "single"
                
                # Stocker la valeur originale pour détecter les changements
                if field_key not in st.session_state.original_values[record["id"]]:
                    st.session_state.original_values[record["id"]][field_key] = str(field_value)
                
                # Vérifier si la valeur a changé
                if field_key in st.session_state:
                    current_value = str(st.session_state[field_key])
                    original_value = str(st.session_state.original_values[record["id"]][field_key])
                    if current_value != original_value:
                        has_changes = True
            
            self.make_form_object(field_config,field_name)

        # Afficher les boutons d'action
        col1, col2 = st.columns([1, 11])
        with col1:
            col3, col4 = st.columns(2)
            with col3:
                # Afficher le bouton save uniquement si des modifications ont été détectées
                if not has_changes:
                    st.button("💾", key=f"{form_key_prefix}save", type="primary", disabled=True)
                else :
                    if st.button("💾", key=f"{form_key_prefix}save", type="primary", disabled=False):
                        self._handle_edit_save(fields_config, record)
            with col4:
                # Le bouton cancel est toujours présent
                if st.button("❌", key=f"{form_key_prefix}cancel"):
                    # Réinitialiser les valeurs
                    if record["id"] in st.session_state.original_values:
                        del st.session_state.original_values[record["id"]]
                    st.session_state.editing_record = {
                        "id": None,
                        "is_editing": False,
                        "incident_type_id": st.session_state.data.incident_type_id
                    }
                    st.rerun()

    def _handle_edit_save(self, fields_config: dict, record: dict) -> None:
        """
        This piece of shit handles saving edited records.
        Now with smart updates - we ain't sending what ain't changed!
        """
        try:
            # Get original values from record
            original_values = {field: record.get(field) for field in fields_config.keys()}
            
            # Build update data with only changed fields
            update_data = self._build_update_data(fields_config, original_values)
            
            if not update_data:
                st.warning("No changes detected")
                return

            logger.info(f"Updating record {record['id']} with {len(update_data)} changed fields")
            logger.debug(f"Update payload: {json.dumps({'record_id': record['id'], 'update_data': update_data}, indent=2, cls=JSONDateEncoder)}")

            # Get the current step data and table master info
            step_data = self.ms_json.extract_sub_dict_from_json(False,self.get_status)
            table_master = step_data.get("tableMaster", {}).get("table")
            
            if not table_master:
                st.error("Table configuration not found") 
                return

            # Get model class and perform update
            ModelClass = self.bl_incident.db.get_class_model(table_master)
            if not ModelClass:
                st.error(f"Invalid table: {table_master}")
                return

            success = self.bl_incident.db.update_record(
                ModelClass,
                record_id=record['id'],
                **update_data
            )

            if success:
                st.success("Record updated successfully! 🎉")
                # Reset edit state
                if record["id"] in st.session_state.original_values:
                    del st.session_state.original_values[record["id"]]
                st.session_state.editing_record = {
                    "id": None,
                    "is_editing": False,
                    "incident_type_id": st.session_state.data.incident_type_id
                }
                st.rerun()
            else:
                st.error("Failed to update record 💩")
                
        except Exception as e:
            logger.error(f"Holy crap, everything's on fire! {str(e)}")
            #logger.exception("Traceback:")
            st.error("Failed to update record")

class JSONDateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)
