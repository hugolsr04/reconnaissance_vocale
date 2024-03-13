# Importation des modules nécessaires pour l'application.
from flask import Flask, request, redirect, url_for, render_template, flash, session, send_file, send_from_directory, jsonify, current_app, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from MySQLdb.cursors import DictCursor
from flask_mysqldb import MySQL
from datetime import datetime
from shutil import rmtree
from docx import Document
import mimetypes
import warnings
import logging
import whisper
import shutil
import os

#Ignore l'avertissement disant la non disponibilité du GPU.
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Configuration de l'application Flask.
app = Flask(__name__)
# Configuration pour la connexion à la base de données MySQL.
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'transcription_db'
app.secret_key = 'b47079d922d6ed7e70d5b1e3b6fc79b3'
app.config['UPLOAD_FOLDER'] = 'uploads'

app.logger.setLevel(logging.DEBUG)

mysql = MySQL(app)

# Initialisation de Flask-Login pour la gestion des sessions utilisateur.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Définition de la classe utilisateur pour Flask-Login.
class User(UserMixin):
    def __init__(self, id, username="", email="", is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin

# Fonction pour charger un utilisateur à partir de l'ID de session.
@login_manager.user_loader
def user_loader(user_id):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (int(user_id),))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user['id'], username=user['username'], email=user['email'], is_admin=user['is_admin'])
    return None

def get_transcription_by_id(transcription_id):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT * FROM transcriptions WHERE id = %s", [transcription_id])
    transcription = cur.fetchone()
    cur.close()
    return transcription

# Route pour la page de connexion.
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Traitement du formulaire de connexion.
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute("SELECT id, password_hash, is_admin FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(id=user['id'], is_admin=user['is_admin'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect')
    return render_template('login.html')

# Route pour la déconnexion.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route pour la création d'un nouvel utilisateur par un administrateur.
@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'administrateur.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Processus de création de l'utilisateur
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        transcriptions_limit = request.form.get('transcriptions_limit', 4)  # Assurez-vous que ce champ existe dans votre formulaire
        password_hash = generate_password_hash(password)

        try:
            cur = mysql.connection.cursor(cursorclass=DictCursor)
            cur.execute("INSERT INTO users (username, email, password_hash, is_admin, transcriptions_limit) VALUES (%s, %s, %s, %s, %s)", (username, email, password_hash, is_admin, transcriptions_limit))
            mysql.connection.commit()
            cur.close()
            flash('Utilisateur créé avec succès.')
        except Exception as e:
            flash(f'Erreur lors de la création de l\'utilisateur: {str(e)}')
        
        return redirect(url_for('list_users'))
    else:
        # Charge et affiche le formulaire de création si la méthode n'est pas POST
        return render_template('create_user.html')

# Route pour afficher la liste des utilisateurs (accessible uniquement par les administrateurs).
@app.route('/admin/list_users')
@login_required
def list_users():
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'administrateur.")
        return redirect(url_for('index'))

    search_query = request.args.get('search', '')
    if search_query:
        search_query = f"%{search_query}%"
        sql_query = "SELECT id, username, email, is_admin, transcriptions_count, transcriptions_limit FROM users WHERE id LIKE %s OR username LIKE %s OR email LIKE %s"
        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute(sql_query, (search_query, search_query, search_query))
    else:
        sql_query = "SELECT id, username, email, is_admin, transcriptions_count, transcriptions_limit FROM users"
        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute(sql_query)

    users_data = cur.fetchall()
    cur.close()
    return render_template('list_users.html', users=users_data)

# Route pour supprimer un utilisateur (et son dossier de transcriptions) par un administrateur.
@app.route('/admin/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'administrateur pour effectuer cette action.")
        return redirect(url_for('list_users'))

    user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    if os.path.exists(user_folder_path):
        try:
            shutil.rmtree(user_folder_path)
            flash(f'Dossier de l\'utilisateur {user_id} supprimé avec succès.')
        except Exception as e:
            flash(f'Erreur lors de la suppression du dossier de l\'utilisateur: {e}')

    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    flash('Utilisateur supprimé avec succès.')
    return redirect(url_for('list_users'))

# Route pour le mot de passe d'un utilisateur par un administrateur.
@app.route('/admin/change_password/<int:user_id>', methods=['POST'])
@login_required
def admin_change_password(user_id):
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'administrateur.")
        return redirect(url_for('index'))

    new_password = request.form['new_password']
    password_hash = generate_password_hash(new_password)

    try:
        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
        mysql.connection.commit()
        flash('Mot de passe mis à jour avec succès.')
    except Exception as e:
        flash(f'Erreur lors de la mise à jour du mot de passe: {str(e)}')
    finally:
        cur.close()

    return redirect(url_for('list_users'))

# Route de la page d'accueil après connexion.
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Route pour démarrer une transcription audio.
@app.route('/transcribe', methods=['POST'])
@login_required
def transcribe():
    # Vérifie le nombre de transcriptions effectuées par l'utilisateur par rapport à sa limite.
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT transcriptions_count, transcriptions_limit FROM users WHERE id = %s", [current_user.id])
    user_info = cur.fetchone()

    # Si la limite est atteinte, arrête le processus et informe l'utilisateur.
    if user_info['transcriptions_count'] >= user_info['transcriptions_limit']:
        session['transcription_in_progress'] = False
        return jsonify({"error": "limit_reached", "message": "Vous avez atteint la limite de transcriptions autorisées. Veuillez contacter l'administrateur."}), 429

    # Récupère le fichier audio à transcrire depuis le formulaire.
    file = request.files['audio_file']
    if not file or file.filename == '':
        session['transcription_in_progress'] = False
        flash("Aucun fichier audio trouvé.")
        return redirect(request.url)

    # Sécurise le nom du fichier et prépare le dossier de destination.
    filename = secure_filename(file.filename)
    audio_folder_name = os.path.splitext(filename)[0]
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
    specific_folder = os.path.join(user_folder, audio_folder_name)

    if not os.path.exists(specific_folder):
        os.makedirs(specific_folder)

    # Enregistre le fichier audio et démarre la transcription.
    audio_path = os.path.join(specific_folder, filename)
    file.save(audio_path)

    try:
        session['transcription_in_progress'] = True
        text = transcribe_audio(request.form['model'], audio_path)
        txt_filename = f"{audio_folder_name}.txt"
        txt_path = os.path.join(specific_folder, txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

        # Met à jour la base de données avec la nouvelle transcription.
        cur.execute("""
            INSERT INTO transcriptions (user_id, audio_filename, text_filename, audio_path, text_path, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (current_user.id, filename, txt_filename, audio_path, txt_path, datetime.now()))

        cur.execute("""
            UPDATE users SET transcriptions_count = transcriptions_count + 1 
            WHERE id = %s
            """, [current_user.id])

        mysql.connection.commit()
        session['transcription_in_progress'] = False

        flash("Transcription réussie.")
    except Exception as e:
        flash(str(e))
    finally:
        cur.close()
    return redirect(url_for('my_transcriptions'))

# Fonction pour effectuer la transcription audio avec le modèle Whisper.
def transcribe_audio(model_name, audio_path):
    model = whisper.load_model(model_name)  # Charge le modèle Whisper spécifié.
    result = model.transcribe(audio_path)  # Effectue la transcription sur le fichier audio.
    return result['text']  # Retourne le texte transcrit.

# Route pour vérifier le statut de la transcription en cours.
@app.route('/check_transcription_status')
def check_transcription_status():
    if not current_user.is_authenticated:
        return jsonify({'error': 'unauthenticated', 'message': 'Utilisateur non connecté'}), 401

    transcription_in_progress = session.get('transcription_in_progress', False)
    return jsonify({'transcription_in_progress': transcription_in_progress})

# Route pour permettre à un administrateur d'ajouter des limites de transcription à un utilisateur.
@app.route("/admin/add_transcriptions/<int:user_id>", methods=['GET', 'POST'])
@login_required
def add_transcriptions(user_id):
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits d'administrateur.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        additional_transcriptions = int(request.form.get('additional_transcriptions', 0))

        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute("UPDATE users SET transcriptions_limit = transcriptions_limit + %s WHERE id = %s", (additional_transcriptions, user_id))
        mysql.connection.commit()
        cur.close()

        flash(f'{additional_transcriptions} transcriptions ajoutées avec succès.')
        return redirect(url_for('list_users'))
 
    return render_template('add_transcriptions.html', user_id=user_id)

# Route pour télécharger les fichiers audio ou texte d'une transcription.
@app.route("/download/<int:transcription_id>/<file_type>")
@login_required
def download(transcription_id, file_type):
    transcription = get_transcription_by_id(transcription_id)
    if not transcription or transcription['user_id'] != current_user.id:
        flash("Accès non autorisé ou transcription introuvable.")
        return redirect(url_for('my_transcriptions'))

    file_path = transcription['audio_path'] if file_type == 'audio' else transcription['text_path']
    if not os.path.exists(file_path):
        flash("Fichier non trouvé.")
        return redirect(url_for('my_transcriptions'))

    mimetype = mimetypes.guess_type(file_path)[0]
    return send_file(file_path, as_attachment=True, mimetype=mimetype, download_name=os.path.basename(file_path))

# Route pour supprimer une transcription et son fichier associé.
@app.route('/delete_transcription/<int:transcription_id>', methods=['POST'])
@login_required
def delete_transcription(transcription_id):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT audio_path, text_path FROM transcriptions WHERE id = %s AND user_id = %s", (transcription_id, current_user.id))
    transcription = cur.fetchone()

    if transcription:
        folder_path = os.path.dirname(os.path.join(app.root_path, transcription['audio_path']))
        try:
            if os.path.exists(folder_path):
                rmtree(folder_path)

            cur.execute("DELETE FROM transcriptions WHERE id = %s", (transcription_id,))
            mysql.connection.commit()
            flash('Transcription et dossier associé supprimés avec succès.')
        except Exception as e:
            flash(f'Erreur lors de la suppression du dossier : {e}')
    else:
        flash('Transcription introuvable ou vous n\'avez pas le droit de la supprimer.')

    cur.close()
    return redirect(url_for('my_transcriptions'))

# Route pour accéder directement à un fichier dans le dossier uploads.
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Fichier non trouvé", 404
    return send_file(file_path, as_attachment=True, download_name=filename)

# Route pour convertir un fichier texte de transcription en document Word.
@app.route('/convert_to_word/<int:transcription_id>')
@login_required
def convert_to_word(transcription_id):
    transcription = get_transcription_by_id(transcription_id)
    if not transcription or transcription['user_id'] != current_user.id:
        flash("Accès non autorisé ou transcription introuvable.")
        return redirect(url_for('my_transcriptions'))

    txt_path = transcription['text_path']
    if not os.path.exists(txt_path):
        flash("Fichier .txt non trouvé.")
        return redirect(url_for('my_transcriptions'))

    docx_filename = os.path.splitext(os.path.basename(txt_path))[0] + '.docx'
    docx_path = os.path.join(os.path.dirname(txt_path), docx_filename)
    doc = Document()
    with open(txt_path, 'r', encoding='utf-8') as file:
        doc.add_paragraph(file.read())
    doc.save(docx_path)

    return send_file(docx_path, as_attachment=True, download_name=docx_filename)

# Route pour afficher les transcriptions récentes de l'utilisateur connecté.
@app.route('/my_transcriptions')
@login_required
def my_transcriptions():
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT id, audio_filename, text_filename, audio_path, text_path, created_at FROM transcriptions WHERE user_id = %s ORDER BY created_at DESC LIMIT 4", [current_user.id])
    transcriptions = cur.fetchall()
    cur.close()
    return render_template('my_transcriptions.html', transcriptions=transcriptions)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Point d'entrée pour exécuter l'application Flask sur un réseau local ou sur un serveur.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)