import streamlit as st
import json, os, uuid
from generate_app.z_apps.specific import base_model
import peewee
from peewee import ForeignKeyField
from loguru import logger

class JSONWizard:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        # Dictionnaire de configuration pour la liste déroulante du source-type en fonction du type
        self.source_type_options = {
            "select": ["enum", "sgbd"],
            "text": ["None","session_var","value"],
            "textarea": ["None","session_var","value"],
            "date": ["None","now"],
            "number": ["None","session_var","value"],
            "file": ["None"],
            "boolean": ["None","session_var","value"],
            "auto": ["None","session_var","value", "sgbd"],
            "hidden": ["None","session_var","value"]
        }
        # Configuration pour l'affichage de la case readOnly
        self.readonly_config = {
            "readonly": ["text", "textarea", "date", "number", "file", "boolean", "hidden"]
        }
        logger.info(f"JSONWizard initialisé avec dossier: {folder_path}")
        self.target_table = None  # nouvelle propriété pour stocker la table cible

    # Nouvelle méthode pour extraire les infos d'un champ depuis le modèle Peewee
    def get_field_info(self, table_name: str, field_name: str) -> dict:
        logger.debug(f"Récupération des infos pour le champ '{field_name}' dans la table '{table_name}'.")
        for obj in base_model.__dict__.values():
            try: 
                if not isinstance(obj, type):
                    continue
                if issubclass(obj, base_model.BaseModel) and hasattr(obj, "_meta"):
                    if obj._meta.table_name == table_name:
                        field_obj = obj._meta.fields.get(field_name)
                        if field_obj:
                            # Mapping pour ForeignKeyField avec pré-sélection via ForeignKeyField.field
                            if isinstance(field_obj, ForeignKeyField):
                                preselected = getattr(field_obj, "field", None) or ""
                                self.target_table = field_obj.rel_model._meta.table_name  # affecter la table cible
                                logger.info(f"Champ ForeignKey détecté pour '{field_name}': table cible '{self.target_table}', preselected '{preselected}'.")
                                return {
                                    "type": "select",
                                    "source-type": "sgbd",
                                    "source": self.target_table,
                                    "field-view": "name", # valeur par défaut
                                    "field-record": preselected
                                }
                            # Autres mappings...
                            return {"type": "text"}
            except Exception:
                logger.exception(f"Erreur lors de la récupération du champ '{field_name}' pour la table '{table_name}'.")
        logger.warning(f"Aucune info trouvée pour le champ '{field_name}' dans la table '{table_name}'.")
        return {}

    def get_table_names(self) -> list:
        tables = []
        for obj in base_model.__dict__.values():
            if not isinstance(obj, type):
                continue
            try:
                if issubclass(obj, base_model.BaseModel) and hasattr(obj, "_meta"):
                    tables.append(obj._meta.table_name)
            except Exception:
                logger.exception("Erreur lors de la récupération du nom d'une table.")
        logger.debug(f"Tables détectées: {tables}")
        return tables

    def get_columns(self, table_name: str) -> list:
        for obj in base_model.__dict__.values():
            if not isinstance(obj, type):
                continue
            try:
                if issubclass(obj, base_model.BaseModel) and hasattr(obj, "_meta"):
                    if obj._meta.table_name == table_name:
                        cols = list(obj._meta.fields.keys())
                        logger.debug(f"Colonnes pour la table '{table_name}': {cols}")
                        return cols
            except Exception:
                logger.exception(f"Erreur lors de la récupération des colonnes de la table '{table_name}'.")
        logger.warning(f"Aucune colonne trouvée pour la table '{table_name}'.")
        return []

    def view_json_files(self):
        st.subheader("Étape 1 : Visualisation")
        st.write("Fichiers JSON disponibles :")
        try:
            json_files = [f for f in os.listdir(self.folder_path) if f.endswith(".json")]
            logger.info(f"{len(json_files)} fichiers JSON trouvés dans '{self.folder_path}'.")
            for file_name in json_files:
                file_path = os.path.join(self.folder_path, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = json.load(f)
                    with st.expander(f"Afficher : {file_name}"):
                        st.json(content)
                    logger.debug(f"Chargement réussi du fichier: {file_name}")
                except Exception:
                    logger.exception(f"Erreur lors de la lecture du fichier {file_name}.")
                    st.error(f"Erreur de lecture sur {file_name}.")
        except Exception:
            logger.exception("Erreur lors de la récupération des fichiers JSON.")
            st.error("Impossible de lister les fichiers JSON.")

    @st.dialog("Confirmer la suppression", width="small")
    def confirm_delete(self, file_path: str, data: dict, selected_rub: str, key: str):
        st.write("Êtes-vous sûr de vouloir supprimer ce champ ?")
        col1, col2 = st.columns(2)
        if col1.button("Oui"):
            try:
                logger.info(f"Suppression du champ '{key}' dans la rubrique '{selected_rub}'.")
                del data[selected_rub]["fields"][key]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                logger.debug(f"Fichier '{file_path}' sauvegardé après suppression.")
                st.success(f"Champ '{key}' supprimé.")
                st.rerun()
            except Exception:
                logger.exception(f"Erreur lors de la suppression du champ '{key}'.")
                st.error("Erreur lors de la suppression du champ.")
        if col2.button("Non"):
            logger.info("Suppression annulée par l'utilisateur.")
            st.rerun()

    def add_field_interface(self):
        """
        Étape 2 (b) : Gestion interactive des 'fields' avec champs dynamiques :
         - Pour un champ de type "select", le source-type (enum ou sgbd) est choisi via un selectbox.
         - Si source-type est "enum", un widget multiselect permet de saisir les options.
         - Si source-type est "sgbd", un selectbox permet de choisir la table source, puis des selectbox pour field_view et field_record.
        """
        st.subheader("Étape 2 (b) : Gestion interactive des 'fields'")
        # ...existing code pour sélectionner fichier et rubrique...
        try:
            json_files = [f for f in os.listdir(self.folder_path) if f.endswith(".json")]
            selected_file = st.selectbox("Choisir un fichier JSON", options=json_files)
            if not selected_file:
                st.warning("Aucun fichier sélectionné.")
                return
            file_path = os.path.join(self.folder_path, selected_file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Fichier '{selected_file}' chargé avec succès.")
        except Exception:
            logger.exception("Erreur lors de la lecture du fichier JSON.")
            st.error("Erreur lors du chargement du fichier.")
            return
        rub_keys = list(data.keys())
        selected_rub = st.selectbox("Choisir la rubrique / status", options=rub_keys)
        if not selected_rub:
            st.warning("Aucune rubrique sélectionnée.")
            return

        st.markdown("### Champs existants dans la rubrique '{}'".format(selected_rub))
        fields_dict = data[selected_rub].get("fields", {})

        # Modification de l'en-tête avec style pour le rendre plus visible
        cols_head = st.columns([1.5, 2, 1.5, 1.5, 1.5, 3, 2])
        header_style = """
            <div style="
                background-color: #f65c0b;
                padding: 10px;
                border-bottom: 1px solid #ccc;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
            ">
                {}
            </div>
        """
        cols_head[0].markdown(header_style.format("Champ"), unsafe_allow_html=True)
        cols_head[1].markdown(header_style.format("Label"), unsafe_allow_html=True)
        cols_head[2].markdown(header_style.format("Type"), unsafe_allow_html=True)
        cols_head[3].markdown(header_style.format("Source-Type"), unsafe_allow_html=True)
        cols_head[4].markdown(header_style.format("ReadOnly"), unsafe_allow_html=True)
        cols_head[5].markdown(header_style.format("Options"), unsafe_allow_html=True)
        cols_head[6].markdown(header_style.format("Actions"), unsafe_allow_html=True)
        
        # Ajout d'un séparateur horizontal pour améliorer la lisibilité
        

        #st.write("---")

        # On définit une fonction locale pour construire la chaîne d'options
        def get_options_str(form: dict) -> str:
            return ", ".join([f"{k}: {v}" for k, v in form.items() if k not in ["type", "label", "readonly", "source-type"] and v])

        # MAJ de l'en-tête avec 7 colonnes
        cols_head = st.columns([1.5, 2, 1.5, 1.5, 1.5, 3, 2])
        #cols_head[0].write("Champ")
        #cols_head[1].write("Label")
        #cols_head[2].write("Type")
        #cols_head[3].write("Source-Type")
        #cols_head[4].write("ReadOnly")
        #cols_head[5].write("Options")
        #cols_head[6].write("Actions")

        # Parcours des champs existants
        for key, field in fields_dict.items():
            form = field.get("form", {})
            options_str = get_options_str(form)
            readonly = form.get("readonly", False)
            st.markdown("<hr style='margin:0px; padding:0px;'/>", unsafe_allow_html=True)
            # Si en mode édition pour cette ligne
            if st.session_state.get("mod_pos") == key:
                edit_cols = st.columns([1.5, 2, 1.5, 1.5, 1.5, 3, 2])
                edit_cols[0].write(key)  # champ non modifiable
                new_label = edit_cols[1].text_input(" ", value=field.get("label", " "), key=f"mod_label_{key}")
                new_type = edit_cols[2].selectbox(" ", options=["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"],
                                                    index=["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"].index(form.get("type", "text")),
                                                    key=f"mod_type_{key}")
                # Pour "select", transformer en selectbox
                if new_type == "select":
                    # Utilisation de la configuration pour source-type avec détermination de l'index par défaut
                    choices = self.source_type_options.get(new_type, [""])
                    default_source = form.get("source-type", choices[0])
                    logger.debug(f"[MOD-{key}] selectbox choices: {choices}, default_source: {default_source}, calculated index: {(choices.index(default_source) if default_source in choices else 0)}")
                    new_source_type = edit_cols[3].selectbox(" ", options=choices,
                        index=(choices.index(default_source) if default_source in choices else 0),
                        key=f"mod_source_{key}", label_visibility="hidden")
                    if new_source_type == "enum":
                        # Correction : calcul de la default et des options de secours
                        default_enum = form.get("source") if isinstance(form.get("source"), list) else []
                        enum_options = default_enum if default_enum else ["Internal", "Wholesaler"]
                        new_options = edit_cols[5].text_input("list_enum", value=", ".join(enum_options), key=f"mod_options_{key}", label_visibility="hidden")
                        new_id_view = edit_cols[5].checkbox("ID view", value=False, key=f"mod_id_view_{key}")
                    elif new_source_type == "sgbd":
                        # Calcul de l'index pour la pré-sélection de la table source
                        # On utilise self.target_table définie dans get_field_info si disponible
                        tab_info = self.get_field_info("tableMaster", "field")
                        table_cible = tab_info.get("source") if tab_info.get("source") else None
                        if table_cible is None:
                            table_cible = form.get("source")  # fallback sur l'ancienne méthode
                        table_list = self.get_table_names()
                        mod_index = table_list.index(table_cible) if table_cible in table_list else 0
                        logger.warning(f"[MOD-{key}] Table source: '{table_cible}' - index calculé: {mod_index}")
                        mod_table = st.selectbox("Table Source", options=table_list, key=f"mod_table_{key}", index=mod_index)
                        mod_cols = self.get_columns(mod_table)
                        mod_field_view = st.selectbox("Field View", options=mod_cols, key=f"mod_field_view_{key}")
                        mod_field_record = st.selectbox("Field Record", options=mod_cols, key=f"mod_field_record_{key}")
                        new_id_view = st.checkbox("ID view", value=False, key=f"mod_id_view_{key}")
                        new_options = {"source": mod_table, "field-view": mod_field_view, "field-record": mod_field_record, "id_view": new_id_view}
                    else:
                        new_options = edit_cols[5].text_input(" ", value=options_str, 
                                                                key=f"mod_options_{key}", label_visibility="hidden")
                        new_id_view = st.checkbox("ID view", value=False, key=f"mod_id_view_{key}")
                else:
                    choices = self.source_type_options.get(new_type, [""])
                    new_source_type = edit_cols[3].selectbox(" ", options=choices, key=f"mod_source_{key}")
                    new_options = edit_cols[5].text_input(" ", value=options_str, key=f"mod_options_{key}")
                
                # Affichage conditionnel de la checkbox readOnly
                if new_type in self.readonly_config["readonly"]:
                    new_readonly = edit_cols[4].checkbox("readonly", value=readonly, key=f"mod_ro_{key}", label_visibility="hidden")
                else:
                    edit_cols[4].empty()
                    new_readonly = False
                with edit_cols[6]:
                    action_cols = st.columns(2)  # 2 sous-colonnes pour aligner horizontalement
                    btn_save = action_cols[0].button("✔️", key=f"save_inline_{key}")
                    btn_cancel = action_cols[1].button("❌", key=f"cancel_inline_{key}")
                    if btn_save:
                        try:
                            # Mise à jour du field
                            field["label"] = new_label
                            field["form"]["type"] = new_type
                            field["form"]["source-type"] = new_source_type
                            field["form"]["readonly"] = new_readonly
                            # Mise à jour selon le type select
                            if new_type == "select":
                                if new_source_type == "enum":
                                    field["form"]["source"] = mod_enum_opts
                                elif new_source_type == "sgbd":
                                    # Stocker les 3 champs dans "options"
                                    field["form"]["options"] = new_options
                                else:
                                    field["form"]["options"] = new_options
                                # --- Transmission de l'option id_view ---
                                field["form"]["id_view"] = new_id_view
                            else:
                                field["form"]["options"] = new_options
                            with open(file_path, "w", encoding="utf-8") as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)
                            logger.info(f"Champ '{key}' modifié dans '{selected_rub}'.")
                            st.success(f"Champ '{key}' modifié.")
                            st.session_state.pop("mod_pos")
                            st.rerun()
                        except Exception:
                            logger.exception(f"Erreur lors de la sauvegarde du champ modifié '{key}'.")
                            st.error("Erreur lors de la modification du champ.")
                    if btn_cancel:
                        logger.info(f"Modification annulée pour le champ '{key}'.")
                        st.session_state.pop("mod_pos")
                        st.rerun()
            else:
                # Affichage normal de la ligne
                row_cols = st.columns([1.5, 2, 1.5, 1.5, 1.5, 3, 2])
                row_cols[0].write(key)
                row_cols[1].write(field.get("label", ""))
                row_cols[2].write(form.get("type", ""))
                row_cols[3].write(form.get("source-type", ""))
                row_cols[4].write(str(readonly))
                row_cols[5].write(options_str)
                # Actions
                action_cols = row_cols[6].columns(3)
                if action_cols[0].button("＋", key=f"add_{key}"):
                    st.session_state.insert_pos = key  # insertion au-dessus de cette ligne
                if action_cols[1].button("✏️", key=f"mod_{key}"):
                    st.session_state.mod_pos = key
                if action_cols[2].button("🗑️", key=f"del_{key}"):
                    logger.info(f"Demande de suppression pour le champ '{key}'.")
                    self.confirm_delete(file_path, data, selected_rub, key)

                # Si insertion inline demandée pour cette ligne
                if st.session_state.get("insert_pos") == key:
                    st.markdown("<hr style='margin:2px 0;'/>", unsafe_allow_html=True)
                    # Définir localement table_master et available_fields
                    table_master = data[selected_rub].get("tableMaster", {}).get("table", "")
                    available_fields = self.get_columns(table_master) if table_master else []
                    # Répartition à 7 colonnes identique à l'en-tête
                    add_cols = st.columns([1.5, 2, 1.5, 1.5, 1.0, 3, 2])
                    # Colonne 0 : "Champ" avec gestion du choix "autre"
                    field_choice = add_cols[0].selectbox("Champ", options=available_fields + ["autre"], key=f"field_choice_{key}")
                    if field_choice == "autre":
                        new_name = add_cols[0].text_input("Nom personnalisé", key=f"custom_field_{key}")
                    else:
                        new_name = field_choice
                        default_info = self.get_field_info(table_master, field_choice)
                    # Colonne 1 : "Label"
                    new_label = add_cols[1].text_input("Label", key=f"new_label_{key}")
                    # Colonne 2 : "Type"
                    new_type = add_cols[2].selectbox("Type",
                        options=["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"],
                        index=(["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"].index(default_info.get("type"))
                               if default_info.get("type") in ["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"] else 0),
                        key=f"new_type_{key}")
                    if new_type == "select":
                        choices = self.source_type_options.get(new_type, [""])
                        # Utiliser default_info pour pré-sélectionner 'sgbd' si le champ est ForeignKeyField
                        default_source = default_info.get("source-type") if default_info.get("source-type") else choices[0]
                        new_source_type = add_cols[3].selectbox("Source-Type", options=choices,
                            index=(choices.index(default_source) if default_source in choices else 0),
                            key=f"new_source_{key}", label_visibility="hidden")
                        new_readonly = add_cols[4].checkbox("ReadOnly", value=False, key=f"new_ro_{key}")
                        if new_source_type == "enum":
                            new_readonly = False
                            add_cols[4].empty()
                            enum_opts = add_cols[5].text_input("Enum Options", key=f"new_enum_opts_{key}")
                            new_options = enum_opts
                            # --- Ajout de la checkbox id_view ---
                            new_id_view = st.checkbox("ID view", value=False, key=f"new_id_view_{key}")
                        elif new_source_type == "sgbd":
                            add_cols[4].empty()
                            with add_cols[5]:
                                st.markdown(
                                    "<style>.stSelectbox label {margin-top: -5px; padding-top: 0px;}</style>",
                                    unsafe_allow_html=True
                                )
                                # Calcul de l'index à partir de la table cible récupérée
                                target_info = self.get_field_info(table_master, field_choice)
                                table_cible = target_info.get("source") if target_info.get("source") else None
                                table_list = self.get_table_names()
                                inline_index = table_list.index(table_cible) if table_cible in table_list else 0
                                logger.warning(f"[INLINE-{key}] Table source: '{table_cible}' - index calculé: {inline_index}")
                                sgbd_table = st.selectbox("Table Source", options=table_list, key=f"new_table_{key}", index=inline_index)
                                cols_list = self.get_columns(sgbd_table)
                                field_view = st.selectbox("Field View", options=cols_list, key=f"new_field_view_{key}")
                                field_record = st.selectbox("Field Record", options=cols_list, key=f"new_field_record_{key}")
                                new_id_view = st.checkbox("ID view", value=False, key=f"new_id_view_{key}")
                            new_options = {"source": sgbd_table, "field-view": field_view, "field-record": field_record, "id_view": new_id_view}
                            new_readonly = False    # <-- Ajout pour garantir une affectation
                        else:
                            new_readonly = add_cols[4].checkbox("readonly", key=f"new_ro_{key}", label_visibility="hidden")
                            new_options = add_cols[5].text_input("Options", key=f"new_options_{key}")
                            new_id_view = st.checkbox("ID view", value=False, key=f"new_id_view_{key}")
                    else:
                        choices = self.source_type_options.get(new_type, [""])
                        new_source_type = add_cols[3].selectbox("Source-Type", options=choices, key=f"new_source_{key}")
                        if new_type in self.readonly_config["readonly"]:
                            new_readonly = add_cols[4].checkbox("readonly", key=f"new_ro_{key}")
                        else:
                            add_cols[4].empty()
                            new_readonly = False
                        new_options = add_cols[5].text_input("Options", key=f"new_options_{key}")
                    with add_cols[6]:
                        action_cols = st.columns(2)
                        btn_save = action_cols[0].button("✔️", key=f"save_inline_{key}")
                        btn_cancel = action_cols[1].button("❌", key=f"cancel_inline_{key}")
                        if btn_save:
                            try:
                                if new_name and new_name not in fields_dict:
                                    sec_key = str(uuid.uuid4())[:12]
                                    new_field = {
                                        "security-key": sec_key,
                                        "label": new_label or "Label",
                                        "form": {
                                            "type": new_type,
                                            "readonly": new_readonly
                                        }
                                    }
                                    if new_type == "select":
                                        new_field["form"]["source-type"] = new_source_type
                                        if new_source_type == "enum":
                                            new_field["form"]["source"] = enum_opts
                                        elif new_source_type == "sgbd":
                                            # Mise à plat des données (pas de nested 'options')
                                            new_field["form"].update(new_options)
                                        else:
                                            new_field["form"]["options"] = new_options
                                        # --- Transmission de l'option id_view ---
                                        new_field["form"]["id_view"] = new_id_view
                                    else:
                                        new_field["form"]["source-type"] = new_source_type
                                    new_fields = {}
                                    inserted = False
                                    for k, v in fields_dict.items():
                                        if k == key and not inserted:
                                            new_fields[new_name] = new_field
                                            inserted = True
                                        new_fields[k] = v
                                    data[selected_rub]["fields"] = new_fields
                                    with open(file_path, "w", encoding="utf-8") as f:
                                        json.dump(data, f, ensure_ascii=False, indent=4)
                                    logger.info(f"Nouveau champ '{new_name}' ajouté en ligne dans '{selected_rub}'.")
                                    st.success(f"Champ '{new_name}' ajouté.")
                                    st.session_state.pop("insert_pos")
                                    st.rerun()
                                else:
                                    logger.warning("Nom manquant ou champ existant lors de l'ajout inline.")
                                    st.warning("Nom manquant ou champ existant.")
                            except Exception:
                                logger.exception("Erreur lors de l'ajout inline d'un nouveau champ.")
                                st.error("Erreur lors de l'ajout du champ.")
                        if btn_cancel:
                            st.session_state.pop("insert_pos")
                            st.rerun()
        # Bouton Ajouter global (insertion en fin)
        st.markdown("### Insérer un nouveau champ en fin")
        if st.button(label="＋", key="global_add"):
            st.session_state.insert_pos = "end"
        if st.session_state.get("insert_pos") == "end":
            st.markdown("<hr style='margin:2px 0;'/>", unsafe_allow_html=True)  # séparateur ajouté pour global
            glob_cols = st.columns([1.5, 2, 1.5, 1.5, 1.0, 3, 2])
            table_master = data[selected_rub].get("tableMaster", {}).get("table", "")
            available_fields = self.get_columns(table_master) if table_master else []
            field_choice = glob_cols[0].selectbox("Champ", options=available_fields + ["autre"], key="global_field_choice")
            if field_choice == "autre":
                new_name = glob_cols[0].text_input("Nom personnalisé", key="global_custom_field")
            else:
                new_name = field_choice
                default_info = self.get_field_info(table_master, field_choice)
            new_label = glob_cols[1].text_input("Label", key="global_new_label")
            new_type = glob_cols[2].selectbox("Type",
                options=["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"],
                index=(["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"].index(default_info.get("type"))
                       if default_info.get("type") in ["text", "textarea", "select", "date", "number", "file", "boolean", "auto", "hidden"] else 0),
                key="global_new_type")
            if new_type == "select":
                choices = self.source_type_options.get(new_type, [""])
                default_source = default_info.get("source-type") if default_info.get("source-type") else choices[0]
                new_source_type = glob_cols[3].selectbox("Source-Type", options=choices,
                    index=(choices.index(default_source) if default_source in choices else 0),
                    key="global_new_source", label_visibility="hidden")
                new_readonly = glob_cols[4].checkbox("ReadOnly", value=False, key="global_new_ro")
                if new_source_type == "enum":
                    new_readonly = False
                    glob_cols[4].empty()
                    enum_opts = glob_cols[5].text_input("Enum Options", key="global_new_enum_opts")
                    new_options = enum_opts
                    # --- Ajout de la checkbox id_view ---
                    new_id_view = st.checkbox("ID view", value=False, key="global_new_id_view")
                elif new_source_type == "sgbd":
                    glob_cols[4].empty()
                    with glob_cols[5]:
                        st.markdown(
                            "<style>.stSelectbox label {margin-top: -5px; padding-top: 0px;}</style>",
                            unsafe_allow_html=True
                        )
                        target_info = self.get_field_info(table_master, field_choice)
                        table_cible = target_info.get("source") if target_info.get("source") else None
                        table_list = self.get_table_names()
                        global_index = table_list.index(table_cible) if table_cible in table_list else 0
                        logger.warning(f"[GLOBAL] Table source: '{table_cible}' - index calculé: {global_index}")
                        sgbd_table = st.selectbox("Table Source", options=table_list, key="global_new_table", index=global_index)
                        cols_list = self.get_columns(sgbd_table)
                        field_view = st.selectbox("Field View", options=cols_list, key="global_new_field_view")
                        field_record = st.selectbox("Field Record", options=cols_list, key="global_new_field_record")
                        new_id_view = st.checkbox("ID view", value=False, key="global_new_id_view")
                    new_options = {"source": sgbd_table, "field-view": field_view, "field-record": field_record, "id_view": new_id_view}
                    new_readonly = False    # <-- Ajout pour garantir une affectation
                else:
                    new_readonly = glob_cols[4].checkbox("ro", key="global_new_ro")
                    new_options = glob_cols[5].text_input("Options", key="global_new_options")
                    new_id_view = st.checkbox("ID view", value=False, key="global_new_id_view")
            else:
                choices = self.source_type_options.get(new_type, [""])
                new_source_type = glob_cols[3].selectbox("Source-Type", options=choices, key="global_new_source")
                if new_type in self.readonly_config["readonly"]:
                    new_readonly = glob_cols[4].checkbox("ro", key="global_new_ro")
                else:
                    glob_cols[4].empty()
                    new_readonly = False
                new_options = glob_cols[5].text_input("Options", key="global_new_options")
            with glob_cols[6]:
                action_cols = st.columns(2)
                btn_save_global = action_cols[0].button("✔️", key="global_save_inline")
                btn_cancel_global = action_cols[1].button("❌", key="global_cancel_inline")
                if btn_save_global:
                    try:
                        if new_name and new_name not in fields_dict:
                            sec_key = str(uuid.uuid4())[:12]
                            new_field = {
                                "security-key": sec_key,
                                "label": new_label or "Label",
                                "form": {
                                    "type": new_type,
                                    "readonly": new_readonly
                                }
                            }
                            if new_type == "select":
                                new_field["form"]["source-type"] = new_source_type
                                if new_source_type == "enum":
                                    new_field["form"]["source"] = enum_opts
                                elif new_source_type == "sgbd":
                                    # Mise à plat des données
                                    new_field["form"].update(new_options)
                                else:
                                    new_field["form"]["options"] = new_options
                                # --- Transmission de l'option id_view ---
                                new_field["form"]["id_view"] = new_id_view
                            else:
                                new_field["form"]["source-type"] = new_source_type
                            data[selected_rub].setdefault("fields", {})[new_name] = new_field
                            with open(file_path, "w", encoding="utf-8") as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)
                            logger.info(f"Nouveau champ global '{new_name}' ajouté dans '{selected_rub}'.")
                            st.success(f"Champ '{new_name}' ajouté.")
                            st.session_state.pop("insert_pos")
                            st.rerun()
                        else:
                            logger.warning("Nom manquant ou champ existant lors de l'ajout global.")
                            st.warning("Nom manquant ou champ existant.")
                    except Exception:
                        logger.exception("Erreur lors de l'ajout global d'un nouveau champ.")
                        st.error("Erreur lors de l'ajout du champ.")
                if btn_cancel_global:
                    st.session_state.pop("insert_pos")
                    st.rerun()
