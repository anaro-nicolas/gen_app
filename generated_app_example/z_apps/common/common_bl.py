from loguru import logger
from typing import List, Optional, Dict, Union, Any
from generate_app.z_apps.common.db_conector3 import *
from generate_app.z_apps.specific.base_model import *

class BusinessLayer:
    def __init__(self):
        self.db = DBConnector3()
        self.model_map = self.db.model_map

    def _get_model_class(self, evaluate: Union[str, BaseModel, Any]) -> Optional[BaseModel]:
        """Get model class safely."""
        if isinstance(evaluate, str):
            return_valid_object = self.model_map.get(evaluate)
            if not return_valid_object:
                logger.error(f"Invalid model class: {evaluate}")
                return None
            return return_valid_object
        elif evaluate not in self.model_map.values():
            logger.error(f"Invalid model class: {evaluate}")
            return None
        return evaluate

    def get_reference_items(self, model_identifier: Union[str, BaseModel]) -> List[BaseModel]:
        """Get reference items by model class or table name"""
        model = self._get_model_class(model_identifier)
        if model is None:
            return []
        
        items = self.db.get_records(model)
        return items if items else []
    

    def create_reference_item(self, table: Optional[Union[BaseModel, str]], data: Optional[Dict[str, Any]]) -> Optional[Any]:
        """Create reference item safely."""
        if not table or not data:
            logger.error("Missing table or data")
            return False
            
        table = self._get_model_class(table)
        if not table:
            logger.error(f"Invalid table: {table}")
            return False
        
        logger.info(f"[BusinessLayer] Creating reference item in {table}: {data}")
        return bool(self.db.create_record(table, **data))

    def delete_reference_item(self, table: BaseModel, item_id: int) -> bool:
        """Delete reference item safely."""
        if not table or not item_id:
            logger.error("Missing table or item_id")
            return False
            
        table = self._get_model_class(table)
        if not table:
            logger.error(f"Invalid table: {table}")
            return False
            
        logger.info(f"[BusinessLayer] Deleting item {item_id} from {table}")
        return bool(self.db.delete_records(table, id=item_id))

    def get_user(self, email: str) -> Optional[Users]:
        """Récupérer les informations d'un utilisateur"""
        logger.info(f"[BusinessLayer] Getting user info: {email}")
        try:
            user = self.db.get_records(Users, email=email)
            return user[0] if user else None
        except Exception as e:
            logger.error(f"[BusinessLayer] Error getting user: {e}")
            raise

    def get_user_roles(self, email: str) -> List[str]:
        """Récupérer les rôles d'un utilisateur"""
        logger.info(f"[BusinessLayer] Getting roles for user: {email}")
        try:
            roles = self.db.get_records(
                'UserRole',
                join={'User': {'email': email}}
            )
            return [role.role_name for role in roles]
        except Exception as e:
            logger.error(f"[BusinessLayer] Error getting user roles: {e}")
            raise

    def verify_user_permission(self, email: str, required_role: str) -> bool:
        """Vérifier si un utilisateur a une permission spécifique"""
        logger.info(f"[BusinessLayer] Verifying {required_role} permission for: {email}")
        try:
            roles = self.get_user_roles(email)
            return required_role in roles
        except Exception as e:
            logger.error(f"[BusinessLayer] Error verifying permission: {e}")
            raise

    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lister les utilisateurs (pour l'admin)"""
        logger.info(f"[BusinessLayer] Listing users: skip={skip}, limit={limit}")
        try:
            users = self.db.get_records(Users, offset=skip, limit=limit)
            # Convertir les objets User en dictionnaires
            return [{
                'username': user.name,
                'email': user.email,
                'profile': user.profile,
                'is_active': user.is_active
            } for user in users]
        except Exception as e:
            logger.error(f"[BusinessLayer] Error listing users: {e}")
            return []

    def _verify_password(self, plain_password: str, hashed_password: str):
        """Vérifier un mot de passe (à implémenter avec hashage)"""
        # TODO: Implémenter la vérification du mot de passe avec bcrypt
        return True  # Placeholder
    
    
