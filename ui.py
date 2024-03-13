# Importe les modules nécessaires pour l'interface utilisateur et la transcription audio.
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from whisper_interface import transcribe_audio

# Définit la classe principale de l'application.
class Application:
    def __init__(self):
        # Initialise l'interface utilisateur principale.
        self.root = tk.Tk()
        self.root.title("Transcription vocale avec Whisper")

        # Définit les variables pour contrôler l'interface utilisateur et stocker les données de l'utilisateur.
        self.model_var = tk.StringVar(value="medium")  # Modèle de transcription par défaut.
        self.transcript = tk.StringVar(value="La transcription apparaîtra ici...")  # Texte transcrit.
        self.audio_path = ""  # Chemin du fichier audio sélectionné.
        self.transcription_status = tk.StringVar(value="En attente de transcription...")  # Statut de la transcription.

        # Crée les widgets de l'interface utilisateur (labels, combobox, boutons, etc.).
        ttk.Label(self.root, text="Sélectionnez le modèle de transcription :").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.model_var, values=["tiny", "base", "small", "medium", "large"], state="readonly").pack(pady=5)
        ttk.Button(self.root, text="Sélectionner un fichier audio", command=self.select_audio_file).pack(pady=5)
        self.transcribe_button = ttk.Button(self.root, text="Lancer la transcription", command=self.start_transcription, state=tk.DISABLED)
        self.transcribe_button.pack(pady=5)
        self.save_button = ttk.Button(self.root, text="Télécharger la transcription", command=self.save_transcription, state=tk.DISABLED)
        self.save_button.pack(pady=5)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=5)
        self.loading_icon = tk.PhotoImage(file="loading.gif")  # Image d'indicateur de chargement (non fournie ici).
        self.loading_label = ttk.Label(self.root, image=self.loading_icon)
        self.loading_label.pack_forget()  # Cache l'indicateur de chargement par défaut.

        # Affiche le statut de la transcription et le texte transcrit.
        ttk.Label(self.root, textvariable=self.transcription_status, wraplength=400).pack(pady=5)
        ttk.Label(self.root, textvariable=self.transcript, wraplength=400).pack(pady=5)

    # Démarre la boucle principale de l'interface utilisateur.
    def run(self):
        self.root.mainloop()

    # Ouvre un dialogue pour sélectionner un fichier audio et active le bouton de transcription si un fichier est sélectionné.
    def select_audio_file(self):
        self.audio_path = filedialog.askopenfilename()
        if self.audio_path:
            self.transcribe_button['state'] = tk.NORMAL
        else:
            self.transcribe_button['state'] = tk.DISABLED

    # Démarre le processus de transcription dans un thread séparé pour ne pas bloquer l'interface utilisateur.
    def start_transcription(self):
        if self.audio_path:
            self.transcription_status.set("Transcription en cours...")
            self.show_loading_indicator()
            threading.Thread(target=self.transcribe, args=(self.model_var.get(), self.audio_path), daemon=True).start()
            self.transcribe_button['state'] = tk.DISABLED

    # Gère la transcription du fichier audio sélectionné et met à jour l'interface utilisateur en conséquence.
    def transcribe(self, model_name, audio_path):
        try:
            text = transcribe_audio(model_name, audio_path)
            self.transcript.set(text)
            self.root.after(0, self.enable_save_button)
            self.transcription_status.set("Transcription terminée.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la transcription : {e}")
        finally:
            self.hide_loading_indicator()

    # Active le bouton de téléchargement une fois la transcription terminée.
    def enable_save_button(self):
        self.save_button['state'] = tk.NORMAL

    # Permet à l'utilisateur de sauvegarder le texte transcrit dans un fichier .txt.
    def save_transcription(self):
        text = self.transcript.get()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Télécharger la transcription")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)
            messagebox.showinfo("Sauvegarde réussie", "La transcription a été téléchargée avec succès.")

    # Affiche ou cache l'indicateur de chargement selon l'état de la transcription.
    def show_loading_indicator(self):
        self.loading_label.pack()

    def hide_loading_indicator(self):
        self.loading_label.pack_forget()

# Exécute l'application si ce script est le point d'entrée principal.
if __name__ == "__main__":
    app = Application()
    app.run()