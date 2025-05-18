from functools import lru_cache
from loguru import logger
import json
from pathlib import Path
from typing import Optional, Dict, Any

from generate_app.z_apps.specific.error_managment import ErrorHandler, ConfigurationError, ValidationError
from generate_app.z_apps.common.validate import ConfigValidator

class MSJsonUtils:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise ConfigurationError(
                message=f"Fichier de configuration non trouvé: {file_path}",
                details={"file_path": file_path}
            )
        self.config_validator = ConfigValidator()
        
    @lru_cache(maxsize=None)
    def load_json_file(self) -> Dict[str, Any]:
        """Charge et valide le fichier JSON de configuration"""
        with ErrorHandler.error_boundary("Erreur lors du chargement de la configuration"):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                logger.info(f"Configuration chargée depuis {self.file_path}")
                return data
            except json.JSONDecodeError as e:
                raise ConfigurationError(
                    message="Format JSON invalide",
                    details={"error": str(e), "file": str(self.file_path)}
                )
            except Exception as e:
                raise ConfigurationError(
                    message="Erreur lors du chargement du fichier",
                    details={"error": str(e), "file": str(self.file_path)}
                )
    
    def extract_sub_dict_from_json(self, clean_cache: bool = False, status: Optional[str] = None) -> Dict[str, Any]:
        """Extrait et valide une section du JSON basée sur le status"""
        if not status:
            raise ValidationError(
                message="Status non défini",
                details={"status": status}
            )
            
        if clean_cache:
            self.load_json_file.cache_clear()
            
        with ErrorHandler.error_boundary(f"Erreur lors de l'extraction des données pour le status: {status}"):
            # Charger les données
            data = self.load_json_file()
            if status not in data:
                raise ValidationError(
                    message=f"Status '{status}' non trouvé dans la configuration",
                    details={"available_status": list(data.keys())}
                )
            
            # Valider la configuration pour ce status
            try:
                validated_config = self.config_validator.validate_json_config(data, status)
                logger.info(f"Configuration validée pour le status: {status}")
                return validated_config
            except Exception as e:
                raise ValidationError(
                    message=f"Configuration invalide pour le status: {status}",
                    details={"error": str(e)}
                )

    def save_json_file(self, data: Dict[str, Any]) -> None:
        """Sauvegarde les données JSON après validation"""
        with ErrorHandler.error_boundary("Erreur lors de la sauvegarde de la configuration"):
            try:
                # Valider toutes les sections du fichier
                for status, config in data.items():
                    self.config_validator.validate_json_config({status: config}, status)
                
                # Sauvegarder le fichier
                with open(self.file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                logger.info(f"Configuration sauvegardée dans {self.file_path}")
                
                # Vider le cache après la sauvegarde
                self.load_json_file.cache_clear()
                
            except Exception as e:
                raise ConfigurationError(
                    message="Erreur lors de la sauvegarde de la configuration",
                    details={"error": str(e)}
                )

    def update_section(self, status: str, update_data: Dict[str, Any]) -> None:
        """Met à jour une section spécifique du JSON"""
        with ErrorHandler.error_boundary(f"Erreur lors de la mise à jour de la section {status}"):
            # Charger les données existantes
            data = self.load_json_file()
            
            # Valider les nouvelles données
            test_config = {status: update_data}
            self.config_validator.validate_json_config(test_config, status)
            
            # Mettre à jour et sauvegarder
            data[status] = update_data
            self.save_json_file(data)
            logger.info(f"Section {status} mise à jour avec succès")

    def delete_section(self, status: str) -> None:
        """Supprime une section du JSON"""
        with ErrorHandler.error_boundary(f"Erreur lors de la suppression de la section {status}"):
            data = self.load_json_file()
            if status not in data:
                raise ValidationError(
                    message=f"Section {status} non trouvée",
                    details={"available_sections": list(data.keys())}
                )
            
            del data[status]
            self.save_json_file(data)
            logger.info(f"Section {status} supprimée avec succès")

    def get_available_status(self) -> list[str]:
        """Retourne la liste des status disponibles"""
        with ErrorHandler.error_boundary("Erreur lors de la récupération des status"):
            data = self.load_json_file()
            return list(data.keys())

# Exemple d'utilisation:
"""
json_utils = MSJsonUtils("config.json")

try:
    # Charger une section
    config = json_utils.extract_sub_dict_from_json(status="Qualify")
    
    # Mettre à jour une section
    json_utils.update_section("Qualify", {
        "tableMaster": {"table": "new_table"},
        "fields": {...}
    })
    
    # Supprimer une section
    json_utils.delete_section("OldSection")
    
except (ValidationError, ConfigurationError) as e:
    logger.error(f"Erreur: {e.message}")
    logger.debug(f"Détails: {e.details}")
"""