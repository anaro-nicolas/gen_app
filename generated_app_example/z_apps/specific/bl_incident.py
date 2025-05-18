import streamlit as st
import uuid, json
import pandas as pd
from loguru import logger
from typing import Dict, List, Optional
from datetime import datetime

from generate_app.z_apps.common.common_bl import BusinessLayer
from generate_app.z_apps.common.db_conector3 import DBConnector3


class Stepping:
    def __init__(self, incident_id: int = None, incident_type: str = None, incident_type_id:int=None, step: int = 1,color:str="#FAFAFA", code:str=None):
        self.incident_id = incident_id
        self.incident_type = incident_type
        self.incident_type_id = incident_type_id
        self.step = step
        self.color = color
        self.code = code

class BLIncident:
    list_definitions = {
        'incident_types':'name',
        'after_sales':'satc',
        'business':'business',
        'contexts':'context',
        'incident_types':'name',
        'product_families':'name',
        'models':'name',
        'occurences':'code',
        'severities':'severity',
        'priorities_m1':'priority_m1',
        'priorities_m2':'priority_m2',
        'sites':'name',
        'state_8d':'code_state',
        'incidents_and_qualifications':'code'
    }
    
    def __init__(self):
        self.bl = BusinessLayer()
        self.db = DBConnector3()
        self.base_model = self.db.base_model
        self.md_inc= self.db.get_class_model('incidents_and_qualifications')
        self.user_id = st.session_state.user.user_id
        self._incidents = []

    def get_options(self, list_name:str, **kwargs) -> Dict:
        options={}
        table_name_objet = self.base_model
        table_name = f"ref_{list_name}"
        if list_name=='incidents_and_qualifications':
            table_name = 'incidents_and_qualifications'
        table_name_objet = self.db.get_class_model(table_name)
        field_list = self.list_definitions[list_name]
        where = None
        if kwargs:
            conditions = []
            # Only handle 'status' and 'type' kwargs
            for key in ('status', 'type'):
                logger.debug(f"Key: {key}= {kwargs[key]}")
                if key in kwargs:
                    conditions.append(getattr(table_name_objet, key) == kwargs[key])
            if conditions:
                where = conditions[0]
                for condition in conditions[1:]:
                    where &= condition
        lists = self.db.get_records(table_name_objet, where)
        
        logger.debug(f"Lists: {lists}")
        if lists is None:
            return []
        for item in lists:
            id=int(item.id)
            value = getattr(item, field_list)
            options[value]=id
        return options
    
    def incidents_and_qualifications(self) -> List[Dict]:
        """Récupérer tous les incidents"""
        model_incidents = self.md_inc
        try:
            incidents = self.db.get_records(model_incidents)
            return incidents
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des incidents: {str(e)}")
            return []
    
    def get_nb_incidents_created(self) -> int:
        status = self.md_inc.status
        return self.get_incidents_and_qualifications_count('Created')
        
    def get_nb_incidents_in_qulify(self) -> int:
        return self.get_incidents_and_qualifications_count('Qualify')
        
    def get_nb_incidents_in_prioritize(self) -> int:
        return self.get_incidents_and_qualifications_count('Prioritize')
        
    def get_nb_incidents_in_resolve(self) -> int:
        return self.get_incidents_and_qualifications_count('Resolv')
    
    def get_nb_incidents_in_report(self) -> int:
        return self.get_incidents_and_qualifications_count('Report')
    def get_nb_incidents_total(self) -> int:
        return self.get_incidents_and_qualifications_count(None)
    def get_nb_incidents_total_user(self,user_id:int) -> int:
        return self.get_incidents_and_qualifications_count(None,user_id)
    
    def get_incidents_and_qualifications_count(self,self_status=None,user_id=None) ->int:
        model_incidents = self.db.get_class_model('incidents_and_qualifications')
        try:
            if self_status is None and user_id is None:
                count = model_incidents.select(model_incidents.id).count() 
            elif self_status is None and user_id is not None:
                count = model_incidents.select(
                    model_incidents.id, 
                    model_incidents.created_by
                ).where(
                    model_incidents.created_by == user_id
                ).count()
            else:
                logger.debug(f"Filter: {self_status}")
                count = model_incidents.select(
                    model_incidents.id, 
                    model_incidents.status
                ).where(
                    model_incidents.status.like(self_status)
                ).count()
            logger.debug(f"Count: {count}") 
            return count
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du nombre d'incidents: {str(e)}")
            return 0
        
    def get_incidents_and_qualifications_by_filter(self,filter:str) ->pd.DataFrame:
        logger.debug(f"Filter: {filter}")
        """Récupérer les incidents filtrés"""
        model_incidents = self.base_model
        model_incidents = self.db.get_class_model('incidents_and_qualifications')
        model_types = self.db.get_class_model('ref_incident_types')
        model_users = self.db.get_class_model('users')
        model_sites = self.db.get_class_model('ref_sites')
        model_product_families = self.db.get_class_model('ref_product_families')
        model_models = self.db.get_class_model('ref_models')
        model_contexts = self.db.get_class_model('ref_contexts')
        model_severities = self.db.get_class_model('ref_severities')
        model_priorities_m1 = self.db.get_class_model('ref_priorities_m1')
        model_priorities_m2 = self.db.get_class_model('ref_priorities_m2')
        """
           model_incidents.status,
               
               

                   model_users,
                model_sites,
                model_product_families,
                model_models,
                model_contexts,
                model_severities
        """
        try:
            incidents = model_incidents.select(
                model_incidents.code,
                model_incidents.ref,
                model_incidents.status,
                model_incidents.status,
                model_types.name.alias('type'),
                model_types.color,
                model_incidents.created_by,
                model_users.name.alias('username'),
                model_users.email,
                model_incidents.prd_or_cmp,
                model_sites.name.alias('site'),
                model_product_families.name.alias('product_family'),
                model_models.name.alias('model'),
                model_incidents.probleme_description,
                model_severities.security.alias('severity'),
                model_priorities_m1.priority_m1,
                model_priorities_m2.priority_m2,
                model_contexts.context.alias('context'),
                model_incidents.d8,
                model_incidents.qrqc_niv1
           
            ).join(
                model_types, 
            ).join(
                model_users, on=(model_incidents.created_by == model_users.id)
            ).left_outer_join(
                model_sites, on=(model_incidents.site == model_sites.id)    
            ).left_outer_join(
                model_product_families, on=(model_incidents.product_family == model_product_families.id)
            ).left_outer_join(
                model_models, on=(model_incidents.model == model_models.id) 
            ).left_outer_join(
                model_contexts, on=(model_incidents.context == model_contexts.id)
            ).left_outer_join(
                model_severities, on=(model_incidents.severity == model_severities.id)
            ).left_outer_join(
                model_priorities_m1, on=(model_incidents.priority_m1 == model_priorities_m1.id)
            ).left_outer_join(
                model_priorities_m2, on=(model_incidents.priority_m2 == model_priorities_m2.id)
                
            ).dicts()
            
            incidents = list(incidents)
            
            df = pd.DataFrame(incidents)
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des incidents filtrés: {str(e)}")
            logger.exception("Traceback")
            return []
    
    def get_incidents_step1(self) -> List[Dict]:
        """Récupérer les incidents de l'étape 1"""
        model_incidents = self.db.get_class_model('incidents_and_qualifications')
        model_incident_types = self.db.get_class_model('ref_incident_types')
        try:
            query = model_incidents.select(
                model_incidents.id,
                model_incidents.code,
                model_incidents.ref,
                model_incidents.type.alias('type_id'),
                model_incident_types.name.alias('type'),
                model_incident_types.color
            ).join(
                model_incident_types, 
            ).where(
                model_incidents.status == 'Created'
            ).dicts()
            return list(query)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des incidents de l'étape 1: {str(e)}")
            return []

    def get_incidents_step2(self) -> List[Dict]:
        pass
    
    def get_incidents_step3(self) -> List[Dict]:
        pass
    
    def get_code_by_id(self,id_type:int) -> str:
        model_type = self.base_model
        model_type = self.db.get_class_model('ref_incident_types')
        try:
            logger.debug(f"New code with type id: {id_type}")
            filter = {'id':id_type}
            type_prefix = self.db.get_records(model_type, **filter)
            logger.debug(f"Type prefix: {type_prefix}")
            prefix = type_prefix[0].prefix
            year = datetime.now().year
            guid = str(uuid.uuid4().fields[-1])[:5]
            code = f"{prefix}_{year}_{guid}"
            logger.debug(f"Code making: {code}")
            return code
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du code: {str(e)}")
            return 'undefined'
            
    def create_state1_incident(self,type:int,ref:str,user_id:int) -> int:
        model_incident = self.base_model
        model_incident = self.db.get_class_model('incidents_and_qualifications')
        try:
            new_code = self.get_code_by_id(type)
            data={
                'type':type,
                'ref':ref,
                'code':new_code,
                'status':'Created',
                'created_by':user_id,
                'detection_date':datetime.now(),
                'cr_date':datetime.now(),
            }
            logger.debug(f"Data for new incident: {data}")
            incident_id = self.db.create_record(model_incident, **data)
            logger.debug(f"New incident created: {incident_id} with code: {new_code}")
            if incident_id:
                return new_code
            else:
                return 0
        except Exception as e:
            logger.error(f"Error in creating incident in step 1: {str(e)}")
            return 0
    
    def update_from_step1_to_step2(self,incident_id:int,qualification_data:Dict,type:str) -> bool:
        model_incident = self.base_model
        model_incident = self.db.get_class_model('incidents_and_qualifications')
        try:
            filter = {'id':incident_id}
            success = self.db.update_record(model_incident,record_id=incident_id, **qualification_data)
            logger.debug(f"Update step 1 to step 2: {success}")
            return success
        except Exception as e:
            logger.error(f"Error in updating incident from step 1 to step 2: {str(e)}")
            return False
        
    def get_color_by_type(self,type:int) -> str:
        model_type = self.db.get_class_model('ref_incident_types')
        try:
            type = self.db.get_records(model_type, id_type=type)[0]
            return type.color
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la couleur: {str(e)}")
            return 'grey'
        
    def qualify_incident(self, incident_id: int, qualification_data: Dict) -> bool:
        """Qualifier un incident existant"""
        try:
            success = self.bl.update_incident_qualification(
                incident_id=incident_id,
                **qualification_data
            )
            logger.info(f"[IncidentManager] Qualified incident ID: {incident_id}")
            return success
        except Exception as e:
            logger.error(f"[IncidentManager] Error qualifying incident: {e}")
            raise

    def get_incident(self, incident_id: int) -> Optional[Dict]:
        """Récupérer un incident spécifique"""
        try:
            return next((inc for inc in self._incidents if inc["id"] == incident_id), None)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'incident {incident_id}: {str(e)}")
            return None

    def update_incident(self, incident_id: int, update_data: Dict) -> bool:
        """Mettre à jour un incident"""
        try:
            for incident in self._incidents:
                if incident["id"] == incident_id:
                    incident.update(update_data)
                    return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'incident {incident_id}: {str(e)}")
            return False

    def delete_incident(self, incident_id: int) -> bool:
        """Supprimer un incident"""
        try:
            self._incidents = [inc for inc in self._incidents if inc["id"] != incident_id]
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'incident {incident_id}: {str(e)}")
            return False
