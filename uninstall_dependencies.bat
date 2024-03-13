@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Désinstallation des dépendances Python pour le projet
echo Désinstallation des dépendances Python pour le projet...
pip uninstall -y openai-whisper Flask Flask-Login Werkzeug flask_mysqldb python-docx mysqlclient setuptools-rust

echo Toutes les désinstallations sont terminées.
pause
