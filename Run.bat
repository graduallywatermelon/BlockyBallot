@echo off
start "FLASK APP" cmd /k "venv\Scripts\activate.bat && set FLASK_APP=service.py && python -m flask run --port 9001"
start "APP" cmd /k "venv\Scripts\activate.bat && python app.py"
start "FLASK APP" cmd /k "venv\Scripts\activate.bat && set FLASK_APP=service.py && python -m flask run --port 9002"
TIMEOUT 3
start "cURL" cmd /k curl -X POST http://127.0.0.1:9002/register_with -H "Content-Type: application/json" -d "{\"node_address\": \"http://127.0.0.1:9001\"}"
