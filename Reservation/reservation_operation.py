import threading
import time
import socket
from datetime import datetime
from hashlib import sha256
import os

class SalleReservation:
    lock = threading.Lock()
    salle_list = ["A", "B", "C"]
    
    def __init__(self):
        self.reservations = {"A": [], "B": [], "C": []}
        self.charger_sauvegarde()  # Dictionnaire sous la forme {"nom_salle": [(debut, fin, professeur)]}
        self.lock = threading.Lock()

    def charger_sauvegarde(self)-> None:
        """Charge les réservations depuis un fichier de sauvegarde."""
        if os.path.exists("historique_reservations.txt"):
            with open("historique_reservations.txt", "r") as fichier:
                for ligne in fichier:
                    nom_salle, debut, fin, numero_telephone, date_reservation = ligne.strip().split(",")
                    debut = datetime.strptime(debut, "%Y-%m-%d %H:%M:%S")
                    fin = datetime.strptime(fin, "%Y-%m-%d %H:%M:%S")
                    date_reservation = datetime.strptime(date_reservation, "%Y-%m-%d %H:%M:%S")
                    self.reservations[nom_salle].append((debut, fin, numero_telephone, date_reservation))

        else:
            with open("historique_reservations.txt", 'w') as file:
                file.write("")

    def verifier_disponibilite(self, nom_salle, debut, fin):
        """Vérifie si une salle est disponible pour une plage horaire donnée."""

        if nom_salle not in SalleReservation.salle_list:
            return False

        for reservation in self.reservations[nom_salle]:
            debut_exist = reservation[0]
            fin_exist = reservation[1]
            if not (fin <= debut_exist or debut >= fin_exist):
                return False
        return True


        

    def reserver_salle(self, nom_salle, debut, fin, numero_telephone) -> bool:
        """Réserve une salle si elle est disponible pour la plage horaire spécifiée."""
        with SalleReservation.lock:
            if self.verifier_disponibilite(nom_salle, debut, fin):
                if nom_salle not in self.reservations.keys():
                    return False, f"La salle  {nom_salle} n'exist pas."
                self.reservations[nom_salle].append((debut, fin, numero_telephone, datetime.now().replace(microsecond=0)))
                self.enregistrer_reservation()
                return True, f"La salle {nom_salle} a été resevé avec de {debut} à {fin} avec succès."
            else:
                return False, f"La salle {nom_salle} est déjà reservé de {debut} à {fin} "

    def annuler_reservation(self, nom_salle, debut, fin, numero_telephone)-> tuple[bool, str]:
        """Annule une reservation si elle est disponible pour la plage horaire spécifiée."""
        with SalleReservation.lock:
            if nom_salle not in self.reservations:
                return False, f"La salle  {nom_salle} n'exist pas."
            for reservation in self.reservations[nom_salle]:
                if reservation[0] == debut and reservation[1] == fin:
                    if reservation[2] == numero_telephone:
                        self.reservations[nom_salle].remove(reservation)
                        self.enregistrer_reservation()
                        return True, f"{self.reservations}"
                    else:
                        return False, f"La salle {nom_salle} à été reservé par {reservation[2]}, seul le propriétaire peut l'annuler."

                    return True, f"La reservation de la salle {nom_salle} a été annulée de {debut} à {fin} avec succès."
            return False, f"La salle {nom_salle} n'a pas de reservation de {debut} à {fin} "
            

    def enregistrer_reservation(self):
        """Enregistre une réservation dans un fichier."""
        with open("historique_reservations.txt", "w") as fichier:
            for nom_salle, reservations in self.reservations.items():
                for debut, fin, numero_telephone, date_reservation in reservations:
                    fichier.write(f"{nom_salle},{debut},{fin},{numero_telephone},{date_reservation}\n")

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

    def sauvegarder_utilisateurs(self) -> None:
        """Sauvegarde les informations des utilisateurs dans un fichier."""
        with GestionUtilisateurs.lock:
            with open(self.fichier, "w") as f:
                for numero_telephone, infos in self.utilisateurs.items():
                    ligne = f"{numero_telephone};{infos['nom']};{infos['prenom']};{infos['mot_de_passe']}\n"
                    f.write(ligne)

    def creer_compte(self, numero_telephone, nom, prenom, mot_de_passe) -> bool:
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

    def authentifier(self, numero_telephone, mot_de_passe) -> bool :
        """Vérifie les informations de connexion de l'utilisateur."""
        with self.lock:
            if numero_telephone in self.utilisateurs:
                hash_mdp = sha256(mot_de_passe.encode()).hexdigest()
                return self.utilisateurs[numero_telephone]["mot_de_passe"] == hash_mdp
            return False

    def changer_mot_de_passe(self, numero_telephone, nouveau_mdp1, nouveau_mdp2) -> tuple[bool, str]:
        """Permet à un utilisateur de changer son mot de passe."""
        with self.lock:
            if nouveau_mdp1 == nouveau_mdp2:
                self.utilisateurs[numero_telephone]["mot_de_passe"] = sha256(nouveau_mdp1.encode()).hexdigest()
                self.sauvegarder_utilisateurs()
                return True, "Mot de passe changé avec succès."
            else:
                return False, "Les nouveaux mots de passe ne correspondent pas."



# Script client pour interagir avec le serveur
def menu(client_socket) -> None:

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
        client_socket.send("Entrez votre nom, prenom, numero de téléphone séparer par des virgule ',' sans espaces: ".encode())
        informations = client_socket.recv(1024).decode()
        if len(informations.split(",")) == 3:
            nom, prenom, numero_telephone = (info.strip() for info in informations.split(","))
        else:
            nom, prenom, numero_telephone = "", "",""
        if ( nom.isalpha() and prenom.isalpha()) and (numero_telephone.isdigit() and len(numero_telephone) == 8 ):
            break
        else:
            time.sleep(0.5)
            client_socket.send(("Une ou plusieurs informations n'ont pas le bon format. #".encode()))
            time.sleep(0.5)
        
    client_socket.send("Entrez votre code pin de 4 chiffres: ".encode())
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
    
    time.sleep(1)
    menu(client_socket)


def interface_authentifier(client_socket):
    client_socket.sendall("Entrez votre numéro de téléphone: ".encode())
    numero_telephone = client_socket.recv(1024).decode()
    while not numero_telephone.isdigit() and len( "".join(numero_telephone.strip().split())) != 8:
        client_socket.sendall("Numéro de téléphone invalide. Réessayez ou tapez (1) pour revenire au menu principal: ".encode())
        numero_telephone = client_socket.recv(1024).decode()
        if numero_telephone == "1":
            menu(client_socket)
        


    client_socket.sendall("Entrez votre code pin de 4 chiffres: ".encode())
    mot_de_passe = client_socket.recv(1024).decode()
    while not mot_de_passe.isdigit() or len(mot_de_passe) != 4:
        client_socket.sendall("Mot de passe invalide. Veuillez choisir un mot de passe composé de 4 chiffres uniquement :".encode())
        mot_de_passe = client_socket.recv(1024).decode()

    authentification = GestionUtilisateurs()

    return authentification.authentifier(numero_telephone, mot_de_passe), numero_telephone



def reserver_salle(client_socket):


    is_authentifie, numero_telephone = interface_authentifier(client_socket)
    if is_authentifie:

        choix = choix_reservation(client_socket)
        if choix == None:
            menu(client_socket)

        nom_salle, debut, fin = choix

        reservation = SalleReservation()
        is_reserve, message = reservation.reserver_salle(nom_salle, debut, fin, numero_telephone)

        if is_reserve == True:
            client_socket.sendall(message.encode())
        else:
            client_socket.sendall(message.encode())
    else:
        client_socket.sendall("Numero de telephone ou code pin incorecte.#".encode())
    time.sleep(1)

    menu(client_socket)

def choix_reservation(client_socket):
    while True:
        while True:
            client_socket.sendall("Entrez le nom de la salle à réserver:  ou (1) pour revenir au menu principal)".encode())
            nom_salle = client_socket.recv(1024).decode()
            if nom_salle == "1":
                return None
            if nom_salle in SalleReservation.salle_list:
                break
            else:
                client_socket.sendall("Nom de salle invalide.#".encode())
                time.sleep(0.5)

    
        while True:
            client_socket.sendall("Entrez la date et l'heure de début (format: YYYY-MM-DD HH:MM): ".encode())
            debut = client_socket.recv(1024).decode()
            if debut == "1":
                return None
            try:
                debut = datetime.strptime(debut, "%Y-%m-%d %H:%M")
                break
            except ValueError:
                client_socket.sendall("Format de date et heure invalide.#".encode())
            
        while True:
            client_socket.sendall("Entrez la date et l'heure de fin (format: YYYY-MM-DD HH:MM): ".encode())
            fin = client_socket.recv(1024).decode()
            if fin == "1":
                return None
            try:
                fin = datetime.strptime(fin, "%Y-%m-%d %H:%M")
                break
            except ValueError:
                client_socket.sendall("Format de date et heure invalide.#".encode())

        if debut < datetime.now() or fin < datetime.now():
            client_socket.sendall("Veuillez choisir une date et heure futur.#".encode())
            continue
        elif debut >= fin:
            client_socket.sendall("La date et heure de fin doivent suivre la date et heure de debut.#".encode())
            continue
        else:
            break

    return nom_salle, debut, fin



def annuler_reservation(client_socket):


    is_authentifie, numero_telephone = interface_authentifier(client_socket)
    if is_authentifie:

        choix = choix_reservation(client_socket)
        if choix == None:
            menu(client_socket)

        nom_salle, debut, fin = choix

        reservation = SalleReservation()
        is_annule, message = reservation.annuler_reservation(nom_salle, debut, fin, numero_telephone)

    time.sleep(1)

    if is_annule == True:
        client_socket.sendall(message.encode())
    else:
        client_socket.sendall(message.encode())

    menu(client_socket)




def afficher_reservations(client_socket):
    """Affiche la table des réservations pour une salle à partir de maintenant."""

    salle_reservation = SalleReservation()
    reservations = salle_reservation.reservations
    professeurs = GestionUtilisateurs()
    professeurs = professeurs.utilisateurs


    with SalleReservation.lock:


        client_socket.sendall("Entrez le nom de la salle à afficher parmis les suivantes: A,B,C (ou (1) pour revenir au menu principal): ".encode())
        nom_salle = client_socket.recv(1024).decode()
        if nom_salle == "1":
            menu(client_socket)
        
        if nom_salle not in SalleReservation.salle_list:
            client_socket.sendall("Nom de salle invalide.#".encode())
            time.sleep(0.5)
            menu(client_socket)
        
        maintenant = datetime.now()
        reservations_futures = [
            (debut, fin, f"{professeurs[numero_telephone]['nom']} {professeurs[numero_telephone]['prenom']}", date_reservation)
            for debut, fin, numero_telephone, date_reservation in reservations[nom_salle]
            if fin > maintenant
        ]

        if not reservations_futures:
            print(f"Aucune réservation future pour la salle {nom_salle}.")
            return
        
        reservations_futures = sorted(reservations_futures,key=lambda x: x[1])

        separateur = "-"*60
        
        client_socket.sendall(f"""Table des réservations pour la salle {nom_salle} (à partir de {maintenant}):\n
{separateur}
{'Début':<20} {'Fin':<20} {'Professeur':<20}
{separateur}#""".encode())
        for debut, fin, professeur, dateç_reservation in reservations_futures:
            client_socket.sendall(f"{debut.strftime('%Y-%m-%d %H:%M'):<20} {fin.strftime('%Y-%m-%d %H:%M'):<20} {professeur:<20}\n".encode())

    client_socket.sendall(separateur[:-1].encode())
    time.sleep(1)
    choix = client_socket.recv(1024).decode()
    menu(client_socket)
        


if __name__ == "__main__":
    menu(client_socket)