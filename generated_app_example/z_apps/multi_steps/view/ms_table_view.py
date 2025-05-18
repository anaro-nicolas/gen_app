from generate_app.z_apps.multi_steps.base.ms_base import *
import streamlit as st
from generate_app.z_apps._config.config_pages import *

class MSTableView(MultiStepBase):
    def __init__(self, config_path: str, step_name: str, clean_cache: bool = True, requires_workflow: bool = True):
        logger.info(f"\n ## Class MSTableView instance with ## \n =>Path:{config_path} \n =>step name: {step_name} \n")
        
        self.config_path = config_path
        super().__init__(config_path, requires_workflow)
        self.set_status(step_name)
        self.status = self.get_status
        
        self.clean_cache = clean_cache
        self.step_data = self.ms_json.extract_sub_dict_from_json(self.clean_cache,self.get_status)

    def set_next_step_master(self, master_id: int) -> None: 
        # ID records are stored in session state
        st.session_state.data.incident_id = master_id
        step = int(st.session_state.data.step)
        step += 1
        st.session_state.data.step = str(step)
        
    def table_view(self, clean_cache: bool = False) -> None:
        #logger.info("\n ## Displaying table view... ## \n")
        try:
            # Initialize edit state if not exists
            color_tab=st.session_state.data.color
            if "editing_record" not in st.session_state:
                st.session_state.editing_record = {
                    "id": None,
                    "is_editing": False
                }
            else:
                #If the fucking incident_type_id is changed about the editing record, so we need to reset the editing record and pfff it's specific. I must be changed it!!!!!
                if "incident_type_id" not in st.session_state.editing_record or st.session_state.data.incident_type_id != st.session_state.editing_record["incident_type_id"]:
                    st.session_state.editing_record = {
                        "id": None,
                        "is_editing": False
                    }
                        
                
            step_data = self.step_data 
            if not step_data:
                return
            master_config = step_data.get("tableMaster", {})
            secondary_config = step_data.get("tableSecondaire", {})
            fields_config = step_data.get("fields", {})
            #logger.debug(f"=========> ******________ Fetching record: {fields_config}")
            next_step = step_data.get("next_step", None)
            
            if next_step is None:
                next_page = None
            else:
                next_page = next_step.get("next_page", None)
            
            if not master_config or not fields_config:
                logger.error("No master table or fields configuration found")
                return
            #logger.warning(f"**********_______Displaying fields_config: {fields_config}")
            # Get display columns configuration
            display_columns = self._get_display_columns(fields_config)
            
            # Add actions column
            display_columns.append(("actions", "Actions", 4))

            # Create header with dynamic columns
            widths = [col[2] for col in display_columns]
            cols = st.columns(widths)
        
            for i, (field_name, label, _) in enumerate(display_columns):
                #background-color: #{color_tab};
                with cols[i]:
                    # Apply custom styles
                    st.markdown(
                        f"""
                        <div style='
                            padding: 5px;
                            marging:0px;
                            font-size: 12px;
                            font-weight: bold;
                            text-align: center;
                        '>
                            {label}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            st.divider()

            # Get master records
            ModelClass = self.bl_incident.db.get_class_model(master_config["table"])
            master_query = ModelClass.select()
            for field, value in master_config.get("where", {}).items():
                master_query = master_query.where(getattr(ModelClass, field) == value)

            records = list(master_query.dicts()) 
            if not records:
                st.info("No records found")
                return

            # Display fields values avec gestion des champs select/sgbd
            btn_next = []
            i=0
            for record in records:
                #logger.debug(f"**********Displaying record: {record}")
                
                cols = st.columns(widths)
                for i, (field_name, _, _) in enumerate(display_columns[:-1]):
                    with cols[i]:
                        def render_field(field_name, record, fields_config):
                            #logger.debug(f"=========> ******________ Fetching field: {field_name}")
                            

                            field_config = fields_config.get(field_name, {})
                            form_config = field_config.get("form", {})
                            
                            if (form_config.get("type") == "select" and 
                                form_config.get("source_type") == "sgbd"):
                                # this the best method to get the display value of the field, else you are the chance
                                #logger.debug(f"=========> ****** Fetching SGBD options for field: {form_config}")
                                display_value = self.ms_helper.get_display_value(
                                    form_config,
                                    record[field_name]
                                )
                                return display_value
                            else:
                                return record.get(field_name, "")

                        display_value = render_field(field_name, record, fields_config)
                        st.markdown(
                            f"""
                            <div style='
                                padding: 5px;
                                marging:0px;
                                font-size: 12px;
                                text-align: center;
                            '>
                                {display_value}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                # Handle actions column
                with cols[-1]:
                    st.markdown("<div class='myCustomButtons'>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        # Edit button
                        edit_disabled = st.session_state.editing_record["is_editing"]

                        if st.button("✏️", 
                                key=f"edit_btn_{record['id']}", 
                                disabled=edit_disabled,
                                help="Edit this record"):
                            st.session_state.editing_record = {
                                "id": record['id'],
                                "is_editing": True,
                                "data": record,
                                "incident_type_id":st.session_state.data.incident_type_id
                            }
                            st.rerun()

                    with col2:
                        # Next step button (disabled while editing)
                        #logger.warning(f"Next step: {step_data}")
                        if "next_step" in step_data:
                            master_id = record['id']
                            master_code = st.session_state.data.code
                            master_color = st.session_state.data.color
                            btn_next.append(
                                st.button(
                                    "➡️", 
                                    key=f"next_{record['id']}", 
                                    disabled=edit_disabled,
                                    on_click=lambda id=master_id: self.set_next_step_master(id)
                                )
                            )
                        
                            
                    
                    with col3:
                        # Delete button (disabled while editing)
                        if st.button("🗑️", 
                                   key=f"delete_{record['id']}", 
                                   disabled=edit_disabled):
                            if self.ms_helper.delete_master_record(master_config["table"], record['id']):
                                st.rerun()
                    
                # Show edit form if this record is being edited
                if (st.session_state.editing_record["is_editing"] and 
                    st.session_state.editing_record["id"] == record['id']):
                    with st.container(border=True):
                        st.info("Editing record...")
                        self._show_edit_form(fields_config, record)

                # Handle secondary table if configured
                if secondary_config:
                    with st.expander("Details"):
                        self._handle_secondary_table_view(
                            secondary_config,
                            master_id=record['id']
                        )
                
                st.divider()
            i+=1
            for btn in btn_next:
                if btn:
                    logger.debug(f"=========> Next button clicked and pages is : {next_page}")
                    st.switch_page(eval(next_page))
                    
        except Exception as e:
            logger.error(f"Failed to display table view: {e}")
            logger.exception("Traceback:")
            #logger.exception("Traceback:")

