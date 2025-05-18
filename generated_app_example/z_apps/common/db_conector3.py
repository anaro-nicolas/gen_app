import os
from loguru import logger
from peewee import *
from datetime import datetime
from typing import List, Optional, Dict, Union, Any, Type
from peewee import Expression
from generate_app.z_apps.specific.base_model import BaseModel, db


class DBConnector3:  # Changed from DBConnector to DBConnector3
    def __init__(self):
        self.base_model_map = self.__generate_model_map()
        self.base_model = BaseModel()

    def __generate_model_map(self) -> Dict[str, Type[BaseModel]]:
        """Generate comprehensive model mapping"""
        models = {}
        for cls in BaseModel.__subclasses__():
            table_name = getattr(cls._meta, 'table_name', None)
            if table_name:
                models[table_name] = cls
        return models
    
    @property
    def model_map(self) -> Dict[str, Type[BaseModel]]:
        return self.base_model_map
    
    def get_class_model(self, model_name: str) -> Type[BaseModel]:
        """Get model class by table name"""
        if model_name in self.base_model_map:
            model = self.base_model_map[model_name]
            #logger.debug(f"Model found: {model_name}, model: {model.__name__}")
            return model
        else:
            logger.error(f"Model not found: {model_name}")
            return None
    

    def make_test_model(self,model_identifier: Union[str, BaseModel])->bool:
        if isinstance(model_identifier, str):
            logger.error(f"Model identifier: {model_identifier} is a string and not base model")
            return False
        else:
            return True
    
    def get_records(self, model_identifier: Union[str, BaseModel], where_clause: Optional[Expression] = None, **filters) -> List[Any]:
        """Get records with enhanced model resolution"""
        try:
            if not self.make_test_model(model_identifier): return
            model_class = model_identifier
            
            query = model_class.select()
            if filters:
                query = query.filter(**filters)
            elif where_clause is not None:
                logger.debug(f"Where clause: {where_clause}")
                logger.debug(f"Where clause content: {str(where_clause.__dict__)}")
                query = query.where(where_clause)
                        
            logger.debug(f"Executing query for {model_class.__name__}")
            results = list(query)
            logger.debug(f"Records : {results}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving records: {e}")
            return []

    def create_record(self, model_identifier: BaseModel, **data) -> Optional[Any]:
        """Create record using either model class or table name"""
        try:
            if not self.make_test_model(model_identifier): return
            model_class = model_identifier
            record = model_class.create(**data)
            return record
        except Exception as e:
            logger.error(f"Error in db connector : creating record: {e}")
            logger.exception("traceback")
            return False

    def update_record(self, model_identifier: Union[str, BaseModel], record_id: int = None, **data) -> bool:
        """Update a record"""
        try:
            if not self.make_test_model(model_identifier): 
                return False
            model_class = model_identifier
            
            # Créer et exécuter la requête de mise à jour
            query = model_class.update(**data).where(model_class.id == record_id)
            rows_modified = query.execute()  # Execute retourne le nombre de lignes modifiées
            
            return rows_modified > 0  # True si au moins une ligne a été modifiée
            
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            return False

    def delete_record(self, model_identifier: Union[str, BaseModel], record_id: int) -> bool:
        """Delete record using either model class or table name"""
        try:
            if not self.make_test_model(model_identifier): return
            model_class = model_identifier

            rows = model_class.delete().where(model_class.id == record_id).execute()
            return rows > 0
        except Exception as e:
            logger.error(f"Error deleting record: {e}")
            return False
        
# Bind models to database
for model in BaseModel.__subclasses__():
    model.bind(db)
