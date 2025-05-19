@echo off
echo Setting up Sistema de Llamadas development environment...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Copy .env.example to .env
copy .env.example .env

REM Initialize database
python init_db.py

echo Setup complete. You can now run the application with 'python run.py' 