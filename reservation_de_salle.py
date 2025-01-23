import threading
import time
import socket
import json
from datetime import datetime
from hashlib import sha256

class SalleReservation:
    def __init__(self):
        self.reservations = {}  # Dictionnaire sous la forme {"nom_salle": [(debut, fin, professeur)]}
        self.lock = threading.Lock()

    def verifier_disponibilite(self, nom_salle, debut, fin):
        """Vérifie si une salle est disponible pour une plage horaire donnée."""
    with self.lock:
        debut = datetime.strptime(debut, "%Y-%m-%d %H:%M")
        fin = datetime.strptime(fin, "%Y-%m-%d %H:%M")

        if nom_salle not in self.reservations:
            return True

        for reservation in self.reservations[nom_salle]:
            debut_exist = datetime.strptime(reservation[0], "%Y-%m-%d %H:%M")
            fin_exist = datetime.strptime(reservation[1], "%Y-%m-%d %H:%M")
            if not (fin <= debut_exist or debut >= fin_exist):
                return False
        return True


    def reserver_salle(self, nom_salle, debut, fin, professeur):
        """Réserve une salle si elle est disponible pour la plage horaire spécifiée."""
    with self.lock:
        debut_dt = datetime.strptime(debut, "%Y-%m-%d %H:%M")
        fin_dt = datetime.strptime(fin, "%Y-%m-%d %H:%M")

        if self.verifier_disponibilite(nom_salle, debut, fin):
            if nom_salle not in self.reservations:
                self.reservations[nom_salle] = []
            self.reservations[nom_salle].append((debut, fin, professeur))
            self.enregistrer_reservation(nom_salle, debut_dt, fin_dt, professeur)
            return True
        else:
            return False


    def enregistrer_reservation(self, nom_salle, debut, fin, professeur):
        """Enregistre une réservation dans un fichier."""
        with open("historique_reservations.txt", "a") as fichier:
            fichier.write(f"{datetime.now()} - {professeur} a réservé la salle {nom_salle} de {debut} à {fin}\n")

class GestionUtilisateurs:
    def __init__(self):
        self.utilisateurs = {}  # Dictionnaire sous la forme {"nom_utilisateur": "hash_mot_de_passe"}
        self.lock = threading.Lock()

    def creer_compte(self, nom_utilisateur, mot_de_passe):
        """Crée un compte utilisateur avec un mot de passe hashé."""
        with self.lock:
            if nom_utilisateur in self.utilisateurs:
                return False
            self.utilisateurs[nom_utilisateur] = sha256(mot_de_passe.encode()).hexdigest()
            return True

    def authentifier(self, nom_utilisateur, mot_de_passe):
        """Vérifie les informations de connexion de l'utilisateur."""
        with self.lock:
            hash_mdp = sha256(mot_de_passe.encode()).hexdigest()
            return self.utilisateurs.get(nom_utilisateur) == hash_mdp

class ServeurReservation:
    def __init__(self, host="localhost", port=12345):
        self.host = host
        self.port = port
        self.systeme_reservation = SalleReservation()
        self.gestion_utilisateurs = GestionUtilisateurs()

    def demarrer(self):
        """Démarre le serveur pour accepter des connexions clients."""
        serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur_socket.bind((self.host, self.port))
        serveur_socket.listen(5)
        print(f"[SERVEUR] En écoute sur {self.host}:{self.port}")

        while True:
            client_socket, adresse = serveur_socket.accept()
            print(f"[CONNEXION] Client connecté : {adresse}")
            thread = threading.Thread(target=self.gerer_client, args=(client_socket,))
            thread.start()

    def gerer_client(self, client_socket):
        """Gère les interactions avec un client connecté."""
        try:
            while True:
                donnees = client_socket.recv(1024).decode()
                if not donnees:
                    break
                requete = json.loads(donnees)
                reponse = self.traiter_requete(requete)
                client_socket.send(json.dumps(reponse).encode())
        except Exception as e:
            print(f"[ERREUR] {e}")
        finally:
            client_socket.close()

    def traiter_requete(self, requete):
        """Traite les requêtes envoyées par les clients."""
        action = requete.get("action")
        if action == "creer_compte":
            nom_utilisateur = requete.get("nom_utilisateur")
            mot_de_passe = requete.get("mot_de_passe")
            if self.gestion_utilisateurs.creer_compte(nom_utilisateur, mot_de_passe):
                return {"status": "success", "message": "Compte créé avec succès."}
            else:
                return {"status": "error", "message": "Nom d'utilisateur déjà pris."}

        elif action == "authentifier":
            nom_utilisateur = requete.get("nom_utilisateur")
            mot_de_passe = requete.get("mot_de_passe")
            if self.gestion_utilisateurs.authentifier(nom_utilisateur, mot_de_passe):
                return {"status": "success", "message": "Authentification réussie."}
            else:
                return {"status": "error", "message": "Nom d'utilisateur ou mot de passe incorrect."}

        elif action == "reserver_salle":
            nom_utilisateur = requete.get("nom_utilisateur")
            nom_salle = requete.get("nom_salle")
            debut = requete.get("debut")
            fin = requete.get("fin")
            if self.systeme_reservation.reserver_salle(nom_salle, debut, fin, nom_utilisateur):
                return {"status": "success", "message": f"Salle {nom_salle} réservée de {debut} à {fin}."}
            else:
                return {"status": "error", "message": "Salle déjà réservée pour cette plage horaire."}

        else:
            return {"status": "error", "message": "Action inconnue."}



class GestionProfesseurs:
    def __init__(self, fichier="professeur.txt"):
        self.fichier = fichier
        self.lock = threading.Lock()
        self.charger_professeurs()

    def charger_professeurs(self):
        """Charge les informations des professeurs depuis un fichier."""
        self.professeurs = {}  # {numero_telephone: {"nom": ..., "prenom": ..., "mot_de_passe": ...}}
        try:
            with open(self.fichier, "r") as f:
                for ligne in f:
                    numero, nom, prenom, mot_de_passe = ligne.strip().split(";")
                    self.professeurs[numero] = {
                        "nom": nom,
                        "prenom": prenom,
                        "mot_de_passe": mot_de_passe
                    }
        except FileNotFoundError:
            with open(self.fichier, "w") as f:  # Crée le fichier s'il n'existe pas
                pass

    def sauvegarder_professeurs(self):
        """Sauvegarde les informations des professeurs dans un fichier."""
        with open(self.fichier, "w") as f:
            for numero, infos in self.professeurs.items():
                ligne = f"{numero};{infos['nom']};{infos['prenom']};{infos['mot_de_passe']}\n"
                f.write(ligne)

    def creer_compte(self, numero, nom, prenom, mot_de_passe):
        """Crée un compte professeur."""
        with self.lock:
            if numero in self.professeurs:
                return False
            self.professeurs[numero] = {
                "nom": nom,
                "prenom": prenom,
                "mot_de_passe": sha256(mot_de_passe.encode()).hexdigest()
            }
            self.sauvegarder_professeurs()
            return True

    def authentifier(self, numero, mot_de_passe):
        """Vérifie les informations de connexion du professeur."""
        with self.lock:
            if numero in self.professeurs:
                hash_mdp = sha256(mot_de_passe.encode()).hexdigest()
                return self.professeurs[numero]["mot_de_passe"] == hash_mdp
            return False

    def changer_mot_de_passe(self, numero, ancien_mdp, nouveau_mdp1, nouveau_mdp2):
        """Permet à un professeur de changer son mot de passe."""
        with self.lock:
            if numero in self.professeurs:
                hash_mdp = sha256(ancien_mdp.encode()).hexdigest()
                if self.professeurs[numero]["mot_de_passe"] == hash_mdp:
                    if nouveau_mdp1 == nouveau_mdp2:
                        self.professeurs[numero]["mot_de_passe"] = sha256(nouveau_mdp1.encode()).hexdigest()
                        self.sauvegarder_professeurs()
                        return True, "Mot de passe changé avec succès."
                    else:
                        return False, "Les nouveaux mots de passe ne correspondent pas."
                else:
                    return False, "Ancien mot de passe incorrect."
            else:
                return False, "Compte introuvable."



# Script client pour interagir avec le serveur
def client():
    host = "localhost"
    port = 12345

    def envoyer_requete(requete):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            client_socket.send(json.dumps(requete).encode())
            reponse = client_socket.recv(1024).decode()
            return json.loads(reponse)

    print("--- Client de Réservation ---")
    while True:
        print("\nOptions :")
        print("1. Créer un compte")
        print("2. Se connecter")
        print("3. Quitter")
        choix = input("Choisissez une option : ")

        if choix == "1":
            nom_utilisateur = input("Nom d'utilisateur : ")
            mot_de_passe = input("Mot de passe : ")
            requete = {
                "action": "creer_compte",
                "nom_utilisateur": nom_utilisateur,
                "mot_de_passe": mot_de_passe
            }
            reponse = envoyer_requete(requete)
            print(reponse.get("message"))

        elif choix == "2":
            nom_utilisateur = input("Nom d'utilisateur : ")
            mot_de_passe = input("Mot de passe : ")
            requete = {
                "action": "authentifier",
                "nom_utilisateur": nom_utilisateur,
                "mot_de_passe": mot_de_passe
            }
            reponse = envoyer_requete(requete)
            print(reponse.get("message"))

            if reponse.get("status") == "success":
                while True:
                    print("\n--- Menu Utilisateur ---")
                    print("1. Réserver une salle")
                    print("2. Déconnexion")
                    choix_user = input("Choisissez une option : ")

                    if choix_user == "1":
                        nom_salle = input("Nom de la salle : ")
                        debut = input("Heure de début (HH:MM) : ")
                        fin = input("Heure de fin (HH:MM) : ")
                        requete = {
                            "action": "reserver_salle",
                            "nom_utilisateur": nom_utilisateur,
                            "nom_salle": nom_salle,
                            "debut": debut,
                            "fin": fin
                        }
                        reponse = envoyer_requete(requete)
                        print(reponse.get("message"))

                    elif choix_user == "2":
                        print("Déconnexion réussie.")
                        break

                    else:
                        print("Option invalide.")

        elif choix == "3":
            print("Fermeture du client.")
            break

        else:
            print("Option invalide.")

if __name__ == "__main__":
    client()

    serveur = ServeurReservation()
    serveur.demarrer()
