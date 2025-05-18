import streamlit as st
from loguru import logger
from generate_app.z_apps.multi_steps.base.ms_base import MultiStepBase

class MSFormView(MultiStepBase):
    def __init__(self, config_path: str, step_name: str, requires_workflow: bool = True):
        # Appel unique au constructeur avec tous les paramètres
        super().__init__(config_path, requires_workflow)
        self.set_status(step_name)
        self.status = self.get_status

    def set_next_step(self):
        st.session_state.data.step += 1

    def form_view(self, clean_cache: bool = False) -> None:
        # Appliquer la couleur de fond uniforme
        uniform_bg_color = "#" + st.session_state.data.color
        st.markdown(f"""
            <style>
            div[data-baseweb="select"] * {{
                background-color: {uniform_bg_color} !important;
            }}
            .st-bx * {{
                background-color: {uniform_bg_color} !important;
            }}
            .stFileUploader section {{
                background-color: {uniform_bg_color} !important;
            }}
            summary {{
                background-color: {uniform_bg_color} !important;
            }}
            .stTextInput input, .stTextArea textarea, .stNumberInput input {{
                background-color: {uniform_bg_color} !important;
            }}
            </style>
            """, unsafe_allow_html=True)

        try:
            step_data = self.ms_json.extract_sub_dict_from_json(clean_cache, self.status)
            #logger.debug(f"Step data loaded: {step_data}")
            if not step_data:
                st.warning("No form data, buddy. Are we lost?")
                logger.warning("No form data found, aborting.")
                return

            # Affichage des champs du formulaire
            fields = step_data.get("fields", {})
            #logger.warning(f"Fields: {fields}")
            for field_key, field_info in fields.items():
                self.make_form_object(field_info, field_key)

            # Affichage éventuel de la table secondaire
            secondary_table_config = step_data.get("tableSecondaire", {})
            logger.debug(f"========> step_data: {step_data}")
            if secondary_table_config:
                table_st = secondary_table_config.get("table", "")
                label_st = secondary_table_config.get("label", "")
                count_records = secondary_table_config.get("count_records", False)
                expander_st = secondary_table_config.get("expander", False)
                
                record_count = ""
                if count_records:
                    record_count = self.ms_helper.get_count_records(table_st, secondary_table_config)
                    
                if expander_st:
                    with st.expander(f"{label_st}{record_count}", expanded=True):
                        self.show_secondary_table(secondary_table_config)
                else:
                    st.markdown(f"### {label_st}{record_count}")
                    self.show_secondary_table(secondary_table_config)
  
            # Bouton de soumission
            table_master = step_data.get("tableMaster", {}).get("table", "")
            label_master = step_data.get("tableMaster", {}).get("label", "")
            logger.info(f"Table master: {table_master}, label master: {label_master}, current status: {self.get_status}")  
            
            # Utilisation des deux notations pour récupérer la configuration du bouton
            form_buttons = step_data.get("form-buttons") or step_data.get("form_buttons")
            # Récupération en testant les deux notations pour next_step
            next_step = step_data.get("next-step") or step_data.get("next_step")
           
            if next_step is None:
                final_step = False
                status = self.get_status
            else:
                final_step = next_step.get("final", next_step.get("final-step", False))
                status = next_step.get("status", self.get_status)
            
            if form_buttons:
                st.divider()
                cols = st.columns([8, 2])
                btn_key = form_buttons.get("security-key") or form_buttons.get("security_key")
                with cols[1]:
                    button_label = form_buttons.get("label", "Submit")
                    # Si l'étape n'est pas finale, on peut modifier le libellé (optionnel)
                    if not final_step:
                        button_label = form_buttons.get("label", "Next")
                    if st.button(button_label, key=btn_key):
                        self._handle_form_submit(form_buttons, table_master, status, label_master)
                        
        except Exception as e:
            logger.error(f"Crap, something exploded in form_view: {e}")
            #logger.exception("Traceback:")