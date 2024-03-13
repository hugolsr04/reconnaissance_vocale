from ui import Application # Importe la classe Application depuis le module ui.py.
import whisper # Importe la bibliothèque whisper pour la reconnaissance vocale.

if __name__ == "__main__": # Vérifie si ce script est exécuté directement (et non importé dans un autre fichier).
    app = Application() # Crée une instance de la classe Application.
    app.run() # Cette méthode est supposée démarrer l'interface graphique de l'application et gérer l'interaction de l'utilisateur.