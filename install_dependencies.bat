@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Mise à jour de pip
echo Mise à jour de pip...
python -m pip install --upgrade pip

:: Installation des dépendances Python pour le projet
echo Installation des dépendances Python pour le projet...
pip install -U openai-whisper
pip install git+https://github.com/openai/whisper.git
pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git
pip install setuptools-rust
pip install Flask Flask-Login Werkzeug flask_mysqldb python-docx mysqlclient

echo Toutes les installations sont terminées.
pause
