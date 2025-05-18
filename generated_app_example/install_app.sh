#!/usr/bin/bash
set -e

# Modify the following variables
USE_POETRY=${USE_POETRY:-true}
APP_PATH=${APP_PATH:-'generate_app'}

############
# Check Python 3.12
############
echo "[Info] Checking for Python 3.12..."
if ! command -v python3.12 &> /dev/null
then
  echo "[Alert] Python 3.12 not found. Installing..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install python@3.12 || {
      echo "[Error] Failed to install Python 3.12."
      exit 1
    }
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update && sudo apt-get install -y python3.12 || {
      echo "[Error] Failed to install Python 3.12."
      exit 1
    }
  else
    echo "[Error] Unsupported operating system."
    exit 1
  fi
fi
echo "[OK] Python 3.12 is available."
python3.12 --version

############
# Check Poetry
############
if [ "$USE_POETRY" = true ]; then
  echo "[Info] Checking for Poetry installation..."
  if ! command -v poetry &> /dev/null
  then
    echo "[Alert] Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3.12 - || {
      echo "[Error] Failed to install Poetry."
      exit 1
    }
    echo "[OK] Poetry installed."
    sleep 5
  else
    echo "[OK] Poetry already installed."
  fi
  # Configure Poetry
  echo "[Info] Configuring local Poetry..."
  poetry config cache-dir ./.caches --local
  poetry config virtualenvs.path {project-dir}/.venv --local
  poetry config virtualenvs.create true --local
  poetry config virtualenvs.in-project true --local
  poetry config --list
  sleep 1
  echo "Poetry configuration complete."
  echo "############################"
  echo "please wait for 5 seconds..."
  sleep 5
  echo "Installing dependencies with poetry..."
  poetry install --no-root
else
  echo "[Info] Poetry usage disabled. Using default application path: $APP_PATH"
  python3.12 -m venv .venv
  source .venv/bin/activate
  pip3 install --upgrade pip
  pip3 install streamlit sqlite3
fi

### END NO MODIFY

############
# Create Application Directories and Files
############
echo "[Info] Creating application directories and files..."
mkdir -p "$APP_PATH"/{classes,interfaces,_db,_config}
touch "$APP_PATH"/webapp.py
touch "$APP_PATH"/api.py
touch "$APP_PATH"/_config/_config.py

# Creating class files
touch "$APP_PATH"/classes/{db_connector3.py,authenticator.py,business_layer.py,incident_manager.py,reporting_manager.py}

# Creating interface files
touch "$APP_PATH"/interfaces/{dashboard_w.py,incident_form_w.py,admin_panel_w.py,report_view_wa.py,incident_service_a.py,user_service_a.py}

echo "[OK] Application structure created."

############
# Install Database if necessary and configuration, update or create config.py file
############
echo "[Info] Configuring SQLite database..."
DB_NAME="database_$RANDOM"
DB_USER="user_$RANDOM"
DB_PASSWORD=$(openssl rand -base64 12)
DB_PATH="$APP_PATH/_db/${DB_NAME}.sqlite"
echo "DB_HOST = 'localhost'" > "$APP_PATH/_config/config.py"
echo "DB_PORT = 9000" >> "$APP_PATH/_config/config.py"
echo "DB_NAME = '$DB_NAME'" >> "$APP_PATH/_config/config.py"
echo "DB_USER = '$DB_USER'" >> "$APP_PATH/_config/config.py"
echo "DB_PASSWORD = '$DB_PASSWORD'" >> "$APP_PATH/_config/config.py"
echo "DB_PATH = '$DB_PATH'" >> "$APP_PATH/_config/config.py"

# Create the SQLite database and tables
if [ ! -f "$DB_PATH" ]; then
  sqlite3 "$DB_PATH" < ./create_database.sql
  echo "[OK] Database configured and tables created."
else
  echo "[Info] Database already exists. Skipping creation."

fi


############
# Final Summary
############
echo "############################"
echo "Setup complete!"
echo "Application Path: $APP_PATH"
echo "Database Path: $DB_PATH"
echo "############################"
