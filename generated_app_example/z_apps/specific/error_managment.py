from enum import Enum
from typing import Optional, Dict, Any
from loguru import logger
import streamlit as st
from contextlib import contextmanager
from peewee import DatabaseError

class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Catégories d'erreurs"""
    VALIDATION = "validation"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    BUSINESS_LOGIC = "business_logic"
    UI = "ui"

class AppError(Exception):
    """Classe de base pour les erreurs de l'application"""
    def __init__(
        self, 
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.severity = severity
        self.category = category
        self.details = details or {}
        super().__init__(message)

class ValidationError(AppError):
    """Erreurs de validation"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            details=details
        )

class DatabaseError(AppError):
    """Erreurs de base de données"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.DATABASE,
            details=details
        )

class ConfigurationError(AppError):
    """Erreurs de configuration"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.CONFIGURATION,
            details=details
        )

class ErrorHandler:
    """Gestionnaire central des erreurs"""
    
    @staticmethod
    def handle_error(error: AppError) -> None:
        """Gère une erreur de l'application"""
        # Log l'erreur avec le bon niveau
        log_message = f"{error.category.value}: {error.message}"
        if error.details:
            log_message += f"\nDétails: {error.details}"
            
        match error.severity:
            case ErrorSeverity.INFO:
                logger.info(log_message)
                st.info(error.message)
            case ErrorSeverity.WARNING:
                logger.warning(log_message)
                st.warning(error.message)
            case ErrorSeverity.ERROR:
                logger.error(log_message)
                st.error(error.message)
            case ErrorSeverity.CRITICAL:
                logger.critical(log_message)
                st.error(f"Erreur critique: {error.message}")

    @staticmethod
    @contextmanager
    def error_boundary(error_message: str = "Une erreur est survenue", show_details: bool = False):
        """Context manager pour la gestion des erreurs"""
        try:
            yield
        except ValidationError as e:
            ErrorHandler.handle_error(e)
        except DatabaseError as e:
            ErrorHandler.handle_error(e)
        except ConfigurationError as e:
            ErrorHandler.handle_error(e)
        except Exception as e:
            # Convertir les erreurs non gérées en AppError
            error = AppError(
                message=error_message,
                severity=ErrorSeverity.ERROR,
                details={"original_error": str(e)} if show_details else None
            )
            ErrorHandler.handle_error(error)

class TransactionManager:
    """Gestionnaire de transactions"""
    
    def __init__(self, database):
        self.database = database
        
    @contextmanager
    def transaction(self):
        """Context manager pour les transactions"""
        try:
            with self.database.atomic() as transaction:
                yield transaction
        except DatabaseError as e:
            logger.error(f"Erreur de transaction: {str(e)}")
            raise DatabaseError(
                message="Erreur lors de l'opération en base de données",
                details={"original_error": str(e)}
            )

# Exemple d'utilisation:
"""
# Dans le code métier:
with ErrorHandler.error_boundary("Erreur lors de la validation du formulaire"):
    validator = ConfigValidator()
    config = validator.validate_json_config(data, "step1")
    
# Pour les transactions:
transaction_manager = TransactionManager(database)
with transaction_manager.transaction():
    # Opérations de base de données
    model.save()
"""