# Conceptor App

## Overview
Conceptor App is a Python-based application designed to validate JSON data against predefined schemas using the `jsonschema` library. It provides a RESTful API for easy integration and validation of JSON structures.

## Project Structure
```
conceptor_app
├── backend
│   ├── classes
│   │   └── model_validator.py
│   ├── api.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd conceptor_app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the FastAPI server:
   ```
   uvicorn backend.api:app --reload
   ```

2. Use the following endpoint to validate JSON data:
   - **POST** `/validate`
     - Request Body:
       ```json
       {
         "workflow": "Qualify",
         "data": {
           // Your JSON data here
         }
       }
       ```
     - Response:
       - If valid:
         ```json
         {
           "message": "JSON structure is valid."
         }
         ```
       - If invalid:
         ```json
         {
           "errors": [
             "Validation Error: <error message> at <path>"
           ]
         }
         ```

## Dependencies
- FastAPI
- jsonschema

## License
This project is licensed under the MIT License.