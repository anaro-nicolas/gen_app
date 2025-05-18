from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from typing import Optional
from pydantic import BaseModel
from classes.model_validator_service import ModelValidatorService
import json
import os
import tempfile

app = FastAPI()
validator_service = ModelValidatorService()

class WorkflowRequest(BaseModel):
    workflow_name: str
    file_path: Optional[str]
    json_data: Optional[dict] = None
    file: Optional[UploadFile] = None

@app.post("/validate-json/")
async def validate_json(payload: WorkflowRequest):
    print(f"payload: {payload}")
    
    # Vérifier que `workflow_name` est fourni
    if not payload.workflow_name :
        raise HTTPException(status_code=400, detail="`workflow_name` is required.")
    else:
        workflow_name = payload.workflow_name
    
    one_params = False

    if payload.file_path:
        file_path = payload.file_path
        one_params = True
    else:
        file_path = None

    if payload.json_data:
        json_data = payload.json_data
        one_params = True
    else:
        json_data = None
    
    if payload.file:
        file = payload.file
        one_params = True
    else:
        file = None

    if not one_params:
        raise HTTPException(status_code=400, detail="At least one of `file_path`, `json_data`, or `file` must be provided.")

    if file_path:
        # Valider JSON à partir d'un chemin de fichier
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"File not found: {file_path}")
        try:
            with open(file_path, "r") as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in the file.")
    elif file:
        # Valider JSON à partir d'un fichier téléchargé
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(await file.read())
            temp_file.close()
            with open(temp_file.name, "r") as f:
                json_data = json.load(f)
            os.unlink(temp_file.name)  # Nettoyer le fichier temporaire
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in the uploaded file.")
    elif json_data:
        # Valider JSON à partir d'un dictionnaire (déjà analysé)
        pass  # Aucun traitement supplémentaire nécessaire

    # Valider les données JSON par rapport au schéma
    errors = validator_service.validate_json(workflow_name, json_data)
    if errors:
        raise HTTPException(status_code=422, detail={"errors": errors})

    return {"message": "JSON is valid"}