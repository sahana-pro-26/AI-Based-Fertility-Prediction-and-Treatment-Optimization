@echo off
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python manage.py runserver
