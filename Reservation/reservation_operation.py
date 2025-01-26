import threading
import time
import socket
import json
from datetime import datetime
from hashlib import sha256
import os
from collections import OrderedDict ##

class SalleReservation:
    lock = threading.Lock()
    def __init__(self):
        self.reservations = {}  # Dictionnaire sous la forme {"nom_salle": [(debut, fin, professeur)]}
        self.lock = threading.Lock()

    def charger_sauvegarde(self):
        """Charge les réservations depuis un fichier de sauvegarde."""
        if os.path.exists("historique_reservations.txt"):
            with open("historique_reservations.txt", "r") as fichier:
                for ligne in fichier:
                    timestamp, professeur.keys[0], nom_salle, debut, fin = ligne.strip().split(",")
                    debut_dt = datetime.strptime(debut, "%Y-%m-%d %H:%M")
                    fin_dt = datetime.strptime(fin, "%Y-%m-%d %H:%M")
                    if nom_salle not in self.reservations:
                        self.reservations[nom_salle] = []
                    self.reservations[nom_salle].append((debut, fin, professeur))

    def verifier_disponibilite(self, nom_salle, debut, fin):
        """Vérifie si une salle est disponible pour une plage horaire donnée."""
        debut = datetime.strptime(debut, "%Y-%m-%d %H:%M")
        fin = datetime.strptime(fin, "%Y-%m-%d %H:%M")

        if nom_salle not in self.reservations:
            return False

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
                    return False
                self.reservations[nom_salle].append((debut, fin, professeur.numero_telephone[0]))
                self.enregistrer_reservation(nom_salle, debut_dt, fin_dt, professeur.numero_telephone[0])
                return True
            else:
                return False


    def enregistrer_reservation(self, nom_salle, debut, fin, professeur_numero):
        """Enregistre une réservation dans un fichier."""
        with open("historique_reservations.txt", "a") as fichier:
            fichier.write(f"{datetime.now()},{professeur_numero},{nom_salle},{debut},{fin}\n")

class GestionUtilisateurs:
    
    lock = threading.Lock()

    def __init__(self, fichier="utilisateur.txt"):
        self.fichier = fichier
        self.lock = threading.Lock()
        self.utilisateurs = {}  # Dictionnaire sous la forme {"numero_telephone": {"nom": ..., "prenom": ..., "mot_de_passe": ...}}
        self.charger_utilisateurs()

    def charger_utilisateurs(self):
        """Charge les informations des utilisateurs depuis un fichier."""
        try:
            with open(self.fichier, "r") as f:
                for ligne in f:
                    numero_telephone, nom, prenom, mot_de_passe = ligne.strip().split(";")
                    self.utilisateurs[numero_telephone] = {
                        "nom": nom,
                        "prenom": prenom,
                        "mot_de_passe": mot_de_passe
                    }
        except FileNotFoundError:
            with open(self.fichier, "w") as f:  # Crée le fichier s'il n'existe pas
                pass

    def sauvegarder_utilisateurs(self):
        """Sauvegarde les informations des utilisateurs dans un fichier."""
        with GestionUtilisateurs.lock:
            with open(self.fichier, "w") as f:
                for numero_telephone, infos in self.utilisateurs.items():
                    ligne = f"{numero_telephone};{infos['nom']};{infos['prenom']};{infos['mot_de_passe']}\n"
                    f.write(ligne)

    def creer_compte(self, numero_telephone, nom, prenom, mot_de_passe):
        """Crée un compte utilisateur avec un mot de passe hashé."""
        with self.lock:
            if numero_telephone in self.utilisateurs:
                return False
            self.utilisateurs[numero_telephone] = {
                "nom": nom,
                "prenom": prenom,
                "mot_de_passe": sha256(mot_de_passe.encode()).hexdigest()
            }
            self.sauvegarder_utilisateurs()
            return True

    def authentifier(self, numero_telephone, mot_de_passe):
        """Vérifie les informations de connexion de l'utilisateur."""
        with self.lock:
            if numero_telephone in self.utilisateurs:
                hash_mdp = sha256(mot_de_passe.encode()).hexdigest()
                return self.utilisateurs[numero_telephone]["mot_de_passe"] == hash_mdp
            return False

    def changer_mot_de_passe(self, numero_telephone, nouveau_mdp1, nouveau_mdp2):
        """Permet à un utilisateur de changer son mot de passe."""
        with self.lock:
            if nouveau_mdp1 == nouveau_mdp2:
                self.utilisateurs[numero_telephone]["mot_de_passe"] = sha256(nouveau_mdp1.encode()).hexdigest()
                self.sauvegarder_utilisateurs()
                return True, "Mot de passe changé avec succès."
            else:
                return False, "Les nouveaux mots de passe ne correspondent pas."




# Script client pour interagir avec le serveur
def menu(client_socket):

    client_socket.sendall("""
    1. Créer un compte
    2. Réserver une salle
    3. Annuler une réservation
    4. Afficher la table des réservations
    5. Changer de mot de passe
    6. Quitter
    """.encode())

    choix = client_socket.recv(1024).decode()

    while choix not in ["1", "2", "3", "4", "5", "6"]:
        client_socket.sendall("Choix invalide. Veuillez réessayer :".encode())
        choix = client_socket.recv(1024).decode()

    if choix == "1":
        creer_compte(client_socket)

    elif choix == "2":
        reserver_salle(client_socket)

    if choix == "3":
        annuler_reservation(client_socket)

    if choix == "4":
        afficher_reservations(client_socket)

    if choix == "5":
        interface_changer_mot_de_passe(client_socket)

    if choix == "6":
        client_socket.sendall("Au revoir !#".encode())
        client_socket.close()


def interface_changer_mot_de_passe(client_socket):
    """ Interface permettant à l'utilisateur de changer de mot de passe """
    is_authentifie, numero_telephone = interface_authentifier()

    if is_authentifie:
        while True:

            client_socket.sendall("Entrez le nouveau code pin: ".encode())
            nouveau_mdp = client_socket.recv(1024).decode()
            while (not nouveau_mdp.isdigit()) and  len(nouveau_mdp) != 4:
                client_socket.sendall("Code pin invalide. Réessayez: ")
                nouveau_mdp = client_socket.recv(1024).decode()
            
            client_socket.sendall("Entrez le nouveau code pin une deuxème fois: ".encode())
            nouveau_mdp2 = client_socket.recv(1024).decode()
            while (not nouveau_mdp2.isdigit()) and  len(nouveau_mdp2) != 4:
                client_socket.sendall("Code pin invalide. Réessayez: ")
                nouveau_mdp2 = client_socket.recv(1024).decode()
       
            is_changed, message = GestionUtilisateurs.changer_mot_de_passe(numero_telephone, nouveau_mdp, nouveau_mdp2)
            client_socket.sendall(f"{message}#".encode())
            if is_changed:
                break
    else:
        client_socket.sendall("Numero de telephone ou code pin incorecte.#".encode())
    
    time.sleep(3)
    menu(client_socket)

            

def creer_compte(client_socket):

    while True:
        client_socket.sendall("Entrez votre nom, prenom, numero de téléphone séparer par des virgule ',' sans espaces: ".encode())
        informations = client_socket.recv(1024).decode()
        nom, prenom, numero_telephone = [info.strip() for info in informations.split(",")]
        client_socket.sendall(f"{nom}, {prenom}, {numero_telephone}#".encode())
        if ( nom.isalpha() and prenom.isalpha()) and (numero_telephone.isdigit() and len(numero_telephone) == 8 ):
            break
        else:
            client_socket.sendall(("Une ou plusieurs informations n'ont pas le bon format.#".encode()))
        
    client_socket.sendall("Entrez votre code pin de 4 chiffres: ".encode())
    mot_de_passe = client_socket.recv(1024).decode()
    while not mot_de_passe.isdigit() or len(mot_de_passe) != 4:
        client_socket.sendall("Mot de passe invalide. Veuillez choisir un mot de passe composé de 4 chiffres uniquement :".encode())
        mot_de_passe = client_socket.recv(1024).decode()

    gestionUtilisateurs = GestionUtilisateurs()
    if numero_telephone in gestionUtilisateurs.utilisateurs.keys():
        client_socket.sendall("Le numéro de téléphone est déjà utiliser pour un autre compte. #".encode())
    else:
        enregistrer = GestionUtilisateurs()
        enregistrer.creer_compte(numero_telephone, nom, prenom, mot_de_passe)
        client_socket.sendall("Compte créé avec succès. #".encode())
    
    time.sleep(3)
    menu(client_socket)



def interface_authentifier(client_socket):
    client_socket.sendall("Entrez votre numéro de téléphone: ".encode())
    numero_telephone = client_socket.recv(1024).decode()
    while not numero_telephone.isdigit() and len( "".join(numero_telephone.strip().split())) != 8:
        client_socket.sendall("Numéro de téléphone invalide. Réessayez ou tapez (1) pour revenire au menu principal: ".encode())
        numero_telephone = client_socket.recv(1024).decode()
        if numero_telephone == "1":
            menu()


    client_socket.sendall("Entrez votre code pin de 4 chiffres: ".encode())
    mot_de_passe = client_socket.recv(1024).decode()
    while not mot_de_passe.isdigit() or len(mot_de_passe) != 4:
        client_socket.sendall("Mot de passe invalide. Veuillez choisir un mot de passe composé de 4 chiffres uniquement :".encode())
        mot_de_passe = client_socket.recv(1024).decode()

    authentification = GestionProfesseurs()

    return authentification.authentifier(numero_telephone, mot_de_passe), numero_telephone



def reserver_salle(client_socket):
    client_socket.sendall("Entrez le nom de la salle à réserver: ".encode())
    nom_salle = client_socket.recv(1024).decode()

    client_socket.sendall("Entrez la date et l'heure de début (format: YYYY-MM-DD HH:MM): ".encode())
    debut = client_socket.recv(1024).decode()

    client_socket.sendall("Entrez la date et l'heure de fin (format: YYYY-MM-DD HH:MM): ".encode())
    fin = client_socket.recv(1024).decode()

    reservation = SalleReservation()
    reponse = reservation.reserver_salle(nom_salle, debut, fin)

    if reponse:
        client_socket.sendall("Salle réservée avec succès.".encode())
    else:
        client_socket.sendall("Salle déjà réservée pour cette plage horaire.".encode())
    menu(client_socket)



def annuler_reservation(client_socket):
    client_socket.sendall("Entrez le nom de la salle à annuler: ".encode())
    nom_salle = client_socket.recv(1024).decode()

    client_socket.sendall("Entrez la date et l'heure de début (format: YYYY-MM-DD HH:MM): ".encode())
    debut = client_socket.recv(1024).decode()

    client_socket.sendall("Entrez la date et l'heure de fin (format: YYYY-MM-DD HH:MM): ".encode())
    fin = client_socket.recv(1024).decode()

    annulation = SalleReservation()

    reponse = annulation.annuler_reservation(nom_salle, debut, fin)

    if reponse:
        client_socket.sendall("Réservation annulée avec succès.".encode())
    else:
        client_socket.sendall("Impossible d'annuler la réservation.".encode())

    menu(client_socket)



def afficher_reservations(client_socket):
    """Affiche la table des réservations qui ne sont pas encore arrivé."""
    client_socket.sendall("Entrez le nom de la salle à afficher: ".encode())
    nom_salle = client_socket.recv(1024).decode()
    affichage = SalleReservation()
    reservations = affichage.afficher_reservations(nom_salle)

    if reservations:
        client_socket.sendall("Table des réservations :".encode())
        for reservation in reservations:
            client_socket.sendall(f"{reservation[0]} - {reservation[1]} : {reservation[2]}".encode())
    else:
        client_socket.sendall("Aucune réservation trouvée.".encode())

    menu(client_socket)



def afficher_reservations_salle(client_socket, nom_salle):
    """Affiche la table des réservations pour une salle à partir de maintenant."""

    salle_reservation = SalleReservation()

    reservations = salle_reservation.reservations
    with self.lock:
        if nom_salle not in reservations:
            print(f"Aucune réservation pour la salle {nom_salle}.")
            return
        
        maintenant = datetime.now()
        reservations_futures = [
            (debut, fin, professeur)
            for debut, fin, professeur in reservations[nom_salle]
            if fin > maintenant
        ]

        if not reservations_futures:
            print(f"Aucune réservation future pour la salle {nom_salle}.")
            return
        
        reservations = sorted(reservations_futures,key=lambda x: x[1])

        separateur = "-"*60 +"#"
        
        client_socket.sendall(f"Table des réservations pour la salle {nom_salle} (à partir de {maintenant}):#".encode())
        client_socket.sendall(f"{'Début':<20} {'Fin':<20} {'Professeur':<20}#".encode())
        client_socket.sendall(separateur.encode())
        for debut, fin, professeur in sorted(reservations_futures, key=lambda x: x[0]):
            client_socket.sendall(f"{debut:<20} {fin:<20} {professeur:<20}".encode())

    choix = ""
    while choix != "1":
        client_socket.sendall("Taper 1 pour retourner au menu".encode())
        choix = client_socket.recv(1024).decode()

    menu(client_socket)
        


if __name__ == "__main__":
    client()

    serveur = ServeurReservation()
    serveur.demarrer()
