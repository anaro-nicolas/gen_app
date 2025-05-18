import json
import uuid
import hashlib
import base64
import argparse
from datetime import datetime
import shutil
import os

def generate_security_key(path_elements):
    """
    Generate a unique security key from path elements.
    Like a ninja in the night, this function creates untraceable field IDs 🥷
    """
    if not path_elements:
        return str(uuid.uuid4())[:12]

    path_string = "-".join(path_elements)
    hash_object = hashlib.sha256(path_string.encode())
    encoded = base64.urlsafe_b64encode(hash_object.digest()).decode()
    return encoded[:12]

def backup_json_file(file_path: str) -> None:
    """
    Creates a backup of the JSON file with timestamp.
    Because shit happens, and we're not taking any chances! 🎲
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.replace(".json", f"_v_prec{timestamp}.json")
    try:
        shutil.copy2(file_path, backup_path)
        print(f"🔄 Backup created: {backup_path}")
    except Exception as e:
        print(f"💀 Failed to create backup: {str(e)}")
        raise

def update_security_keys(json_data, path=[]):
    """
    Recursively updates the JSON structure with generated security keys.
    Like a drunk locksmith, we're replacing all the keys! 🔑
    """
    if isinstance(json_data, dict):
        # If we're in a field definition, check/update security-key
        if "form" in json_data and isinstance(json_data["form"], dict):
            current_path = path[:]  # Copy current path
            security_key = generate_security_key(current_path)
            json_data["security_key"] = security_key
            print(f"🔐 Generated/Updated security key for {' -> '.join(current_path)}: {security_key}")

        # Continue recursion
        for key, value in json_data.items():
            current_path = path + [key]
            if isinstance(value, dict):
                update_security_keys(value, current_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        update_security_keys(item, current_path + [str(i)])

    return json_data

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Update JSON file with security keys")
    parser.add_argument("file_path", help="Path to the input JSON file")
    args = parser.parse_args()

    file_path = args.file_path
    
    try:
        # Create backup first
        backup_json_file(file_path)
        
        # Load the JSON file
        print(f"📂 Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Update security keys
        updated_json_data = update_security_keys(json_data)

        # Save the updated JSON back to original file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(updated_json_data, file, indent=4, ensure_ascii=False)

        print(f"✅ Successfully updated security keys in: {file_path}")

    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        raise

if __name__ == "__main__":
    main()
