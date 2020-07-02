@echo off

cd "venv\Scripts"
call activate

cd "..\.."
set FLASK_APP=flaskr
set FLASK_ENV=development
