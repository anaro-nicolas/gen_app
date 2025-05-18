from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from loguru import logger
from peewee import ForeignKeyField

class FieldFormConfig(BaseModel):
    """Configuration d'un champ de formulaire"""
    model_config = ConfigDict(populate_by_name=True)
    
    type: str
    source_type: Optional[str] = Field(None, alias='source_type')
    source: Optional[Union[str, List[str], Dict[str, Any]]] = None
    readonly: bool = False
    field_view: Optional[str] = Field(None, alias='field-view')
    field_record: Optional[str] = Field(None, alias='field-record')
    options: Optional[Dict[str, Any]] = None
    where: Optional[Dict[str, Any]] = None
    view_id: Optional[bool] = False

    @field_validator('type')
    @classmethod
    def validate_field_type(cls, v: str) -> str:
        valid_types = ['text', 'textarea', 'select', 'date', 'number', 'file', 'boolean', 'auto', 'hidden']
        if v not in valid_types:
            raise ValueError(f"Type de champ invalide. Types autorisés: {valid_types}")
        return v

    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v: Optional[str], info) -> Optional[str]:
        if not v:
            return v
        valid_source_types = ['enum', 'sgbd', 'session_var', 'value', 'None', 'now']
        if v not in valid_source_types:
            raise ValueError(f"Type de source invalide. Types autorisés: {valid_source_types}")
        
        # Validation spécifique pour le type 'select'
        field_type = info.data.get('type')
        if field_type == 'select' and v not in ['enum', 'sgbd']:
            raise ValueError("Pour un champ 'select', source_type doit être 'enum' ou 'sgbd'")
        return v

class FieldConfig(BaseModel):
    """Configuration complète d'un champ"""
    model_config = ConfigDict(populate_by_name=True)
    
    security_key: str = Field(..., alias='security-key')
    label: str
    form: FieldFormConfig

class TableMasterConfig(BaseModel):
    """Configuration de la table principale"""
    model_config = ConfigDict(populate_by_name=True)
    
    table: str
    label: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    color: Optional[str] = None
    update: Optional[Dict[str, Any]] = None

    @field_validator('table')
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de la table ne peut pas être vide")
        return v

class TableSecondaireConfig(BaseModel):
    """Configuration de la table secondaire"""
    model_config = ConfigDict(populate_by_name=True)
    
    table: str
    label: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    relation: str  # Champ liant la table secondaire à la table principale, requis
    expander: Optional[bool] = False
    count_records: Optional[bool] = False
    fields: Dict[str, FieldConfig]  # Configuration des champs de la table secondaire, requise

    @field_validator('table')
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de la table secondaire ne peut pas être vide")
        return v

    @field_validator('relation')
    @classmethod
    def validate_relation(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le champ relation est requis pour la table secondaire")
        return v

    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v: Dict[str, FieldConfig]) -> Dict[str, FieldConfig]:
        if not v:
            raise ValueError("La configuration des champs pour la table secondaire ne peut pas être vide")
        return v

class NextStepConfig(BaseModel):
    """Configuration de l'étape suivante"""
    model_config = ConfigDict(populate_by_name=True)
    
    step: Dict[str, Union[int, str]]
    entity_id: Dict[str, str]
    incident_type: Dict[str, str]
    incident_type_id: Dict[str, Union[int, str]]
    color: Dict[str, str]
    next_page: Optional[str] = Field(None, alias='next-page')
    step_final: bool = Field(False, alias='step-final')

    @field_validator('step')
    @classmethod
    def validate_step(cls, v: Dict[str, Union[int, str]]) -> Dict[str, Union[int, str]]:
        if 'value' not in v or 'session-var' not in v:
            raise ValueError("Le dictionnaire step doit contenir 'value' et 'session-var'")
        return v

class FormButtonConfig(BaseModel):
    """Configuration des boutons du formulaire"""
    model_config = ConfigDict(populate_by_name=True)
    
    security_key: str = Field(..., alias='security-key')
    label: str
    form_submit: Dict[str, str] = Field(..., alias='form-submit')

    @field_validator('form_submit')
    @classmethod
    def validate_form_submit(cls, v: Dict[str, str]) -> Dict[str, str]:
        if 'type' not in v:
            raise ValueError("Le dictionnaire form_submit doit contenir un champ 'type'")
        return v

class StepConfig(BaseModel):
    """Configuration complète d'une étape"""
    model_config = ConfigDict(populate_by_name=True)
    
    tableMaster: TableMasterConfig
    fields: Dict[str, FieldConfig]
    tableSecondaire: Optional[TableSecondaireConfig] = None
    next_step: Optional[NextStepConfig] = Field(None, alias='next-step')
    form_buttons: Optional[FormButtonConfig] = Field(None, alias='form-buttons')

class ConfigValidator:
    """Classe principale de validation des configurations"""
    
    @staticmethod
    def validate_json_config(config_data: dict, step_name: str) -> dict:
        """
        Valide une configuration JSON pour une étape donnée.
        
        Args:
            config_data: Données de configuration JSON.
            step_name: Nom de l'étape à valider.
            
        Returns:
            dict: Configuration validée.
            
        Raises:
            ValidationError: Si la validation échoue.
        """
        try:
            # Valider la configuration de l'étape
            if step_name not in config_data:
                raise ValueError(f"Étape '{step_name}' non trouvée dans la configuration")
            
            step_config = config_data[step_name]
            validated_config = StepConfig(**step_config)
            
            logger.info(f"Configuration validée avec succès pour l'étape: {step_name}")
            return validated_config.model_dump()
            
        except Exception as e:
            logger.error(f"Erreur de validation pour l'étape {step_name}: {str(e)}")
            raise

class DBValidator:
    """Validation des opérations de base de données"""
    
    @staticmethod
    def validate_table_exists(db_connector, table_name: str) -> bool:
        """Vérifie qu'une table existe dans la base de données."""
        try:
            model_class = db_connector.get_class_model(table_name)
            return model_class is not None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la table {table_name}: {str(e)}")
            return False

    @staticmethod
    def validate_field_exists(db_connector, table_name: str, field_name: str) -> bool:
        """Vérifie qu'un champ existe dans une table."""
        try:
            model_class = db_connector.get_class_model(table_name)
            if model_class is None:
                return False
            return hasattr(model_class, field_name)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du champ {field_name}: {str(e)}")
            return False

    @staticmethod
    def validate_foreign_key(db_connector, table_name: str, field_name: str, ref_table: str) -> bool:
        """Vérifie la validité d'une clé étrangère."""
        try:
            model_class = db_connector.get_class_model(table_name)
            ref_model = db_connector.get_class_model(ref_table)
            if not all([model_class, ref_model]):
                return False
                
            field = getattr(model_class, field_name, None)
            if field is None:
                return False
                
            # Vérifier si le champ est une clé étrangère vers la bonne table
            return isinstance(field, ForeignKeyField) and field.rel_model == ref_model
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la clé étrangère {field_name}: {str(e)}")
            return False