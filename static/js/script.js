// Ce code s'exécute une fois que le DOM de la page est complètement chargé.
document.addEventListener('DOMContentLoaded', function () {
    // Récupère plusieurs éléments du DOM pour les manipuler ultérieurement.
    var transcriptionForm = document.getElementById('transcriptionForm'); // Le formulaire de transcription.
    var loadingIndicator = document.getElementById('loadingIndicator'); // L'indicateur de chargement.
    var downloadContainer = document.getElementById('downloadContainer'); // Le conteneur pour les liens de téléchargement.
    var flashMessages = document.getElementById('flash-messages'); // Vérifiez si des messages flash sont présents

    if (flashMessages && flashMessages.innerHTML.trim() !== '') {
        showPopup(); // Affiche le popup si des messages flash existent
    }

    // Vérifie si une transcription est en cours dès le chargement de la page.
    if (loadingIndicator) {
        checkTranscriptionStatus();
    }

    // Ajoute un écouteur d'événement pour gérer la soumission du formulaire de transcription.
    if (transcriptionForm) {
        transcriptionForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Empêche le comportement par défaut de soumission du formulaire.
            startTranscription(); // Lance la fonction de transcription.
        });
    }

    // Définit la fonction pour commencer la transcription.
    function startTranscription() {
        var formData = new FormData(transcriptionForm); // Crée un objet FormData avec les données du formulaire.

        showLoading(true); // Affiche l'indicateur de chargement.

        // Effectue une requête POST au serveur pour démarrer la transcription avec les données du formulaire.
        fetch('/transcribe', {
            method: 'POST',
            body: formData,
        })
            .then(handleResponse) // Traite la réponse du serveur.
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect; // Redirige l'utilisateur si nécessaire.
                }
                showLoading(false); // Cache l'indicateur de chargement.
            })
            .catch(error => {
                console.error('Erreur:', error); // Affiche une erreur en cas de problème.
                showLoading(false);
            });
    }

    // Fonction pour vérifier l'état de la transcription en cours.
    function checkTranscriptionStatus() {
        fetch('/check_transcription_status')
            .then(handleResponse)
            .then(data => {
                showLoading(data.transcription_in_progress); // Met à jour l'indicateur de chargement en fonction de l'état de la transcription.
            })
            .catch(error => {
                console.error('Erreur lors de la vérification de l\'état de transcription:', error);
                showLoading(false);
            });
    }

    // Fonction pour traiter la réponse du serveur.
    function handleResponse(response) {
        if (!response.ok) {
            throw new Error("Erreur de réponse du serveur"); // Lance une erreur si la réponse n'est pas OK.
        }
        return response.json(); // Convertit la réponse en JSON.
    }

    // Fonction pour montrer ou cacher l'indicateur de chargement.
    function showLoading(show) {
        if (loadingIndicator) loadingIndicator.style.display = show ? 'block' : 'none'; // Affiche ou cache l'indicateur.
        if (downloadContainer) downloadContainer.style.display = !show ? 'block' : 'none'; // Affiche ou cache le conteneur de téléchargement.
    }
});