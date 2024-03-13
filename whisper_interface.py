import whisper  # Importe la bibliothèque Whisper d'OpenAI pour la reconnaissance vocale.
import os  # Importe le module os pour interagir avec le système de fichiers.

def transcribe_audio(model_name, audio_path):
    # Cette fonction charge le modèle Whisper spécifié, transcrit le fichier audio donné,
    # et sauvegarde le texte transcrit dans un fichier .txt.
    model = whisper.load_model(model_name)  # Charge le modèle Whisper spécifié par model_name.
    result = model.transcribe(audio_path)  # Transcrit le fichier audio spécifié par audio_path.
    text = result['text']  # Extrait le texte transcrit à partir du résultat.

    txt_filename = os.path.splitext(os.path.basename(audio_path))[0] + '.txt'
    # Crée le nom du fichier texte en remplaçant l'extension du fichier audio par .txt.
    txt_path = os.path.join('uploads', txt_filename)
    # Construit le chemin complet du fichier texte à sauvegarder dans le dossier 'uploads'.
    
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)  # Écrit le texte transcrit dans le fichier texte.

    return txt_filename  # Retourne le nom du fichier texte créé.