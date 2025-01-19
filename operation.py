import threading
import socket
import os
import random



class Client:
    
    numero_compte = random.randint(100000, 999999)

    def __init__(self, nom: str = "", prenom: str = "", numero_telephone: str = "", type_compte: str = "",
            statut: str = "actif", solde: float = 0, code_pin: str = "0000"):
        self.nom = nom
        self.prenom = prenom
        self.numero_telephone = numero_telephone
        self.type_compte = type_compte
        self.statut = statut
        self.solde = solde
        self.code_pin = code_pin
        self.numero_compte = Client.numero_compte
        Client.numero_compte += 1

    def __str__(self):
        return f"{self.numero_compte} {self.nom} {self.prenom} {self.numero_telephone} {self.type_compte} {self.statut} {self.solde}"
    
    def to_dict(self):
        return {
            "numero_compte": self.numero_compte,
            "nom": self.nom,
            "prenom": self.prenom,
            "numero_telephone": self.numero_telephone,
            "type_compte": self.type_compte,
            "statut": self.statut,
            "solde": self.solde,
            "code_pin": self.code_pin
        }

    def from_dict(self, ligne):
        self.numero_compte = ligne["numero_compte"]
        self.nom = ligne["nom"]
        self.prenom = ligne["prenom"]  
        self.numero_telephone = ligne["numero_telephone"]
        self.type_compte = ligne["type_compte"]
        self.statut = ligne["statut"]
        self.solde = ligne["solde"]
        self.code_pin = ligne["code_pin"]

    def fermerture_compte(self):
        self.statut = "ferme"
        Sauvegarde.ecrire_client(self)
        print(f"Votre compte de numéro {self.numero_compte} a été fermé")





class Sauvegarde: 

    # Fonction pour ajouter ou mettre à jour un client dans le fichier client.txt
    @staticmethod
    def ecrire_client(client: Client, montant: float = 0,  is_transaction = False) -> None:
        """Cette fonction ajoute ou met à jour un client dans le fichier client.txt"""
        clients = Sauvegarde.lire_clients()
        client_existant = False

        # Mettre à jour le client si son numéro de compte existe déjà
        for i, client_dictionnaire in enumerate(clients):
            if client_dictionnaire["numero_compte"] == client.numero_compte:
                if not client_dictionnaire["statut"] == "actif" and is_retrait:
                    return "Compte bloqué"

                if is_transaction :
                    if float(client_destinataire["solde"]) + montant < 0:
                        print("Solde insufisant")
                        return False
                    else:
                        client.solde += montant
                    

                clients[i] = client.to_dict()
                client_existant = True
                break

        if not client_existant:
            clients.append(client.to_dict())

        # Écriture des clients dans le fichier
        with open("client.txt", "w", encoding="UTF-8") as fichier:
            for client_ in clients:
                fichier.write(f"{",".join([str(i) for i in client_.values()])}" + "\n")

    # Fonction pour lire tous les clients depuis le fichier client.txt
    @staticmethod
    def lire_clients() -> list:
        """Cette fonction lit les clients depuis le fichier client.txt et les retourne sous forme de liste de dictionnaires"""
        clients = []
        if os.path.exists("client.txt"):
            with open("client.txt", "r") as fichier:
                for ligne in fichier:
                    client = {
                        "numero_compte": int(ligne.strip().split(",")[0]),
                        "nom":  ligne.strip().split(",")[1],
                        "prenom": ligne.strip().split(",")[2],
                        "numero_telephone": ligne.strip().split(",")[3],
                        "type_compte": ligne.strip().split(",")[4],
                        "statut": ligne.strip().split(",")[5],
                        "solde": float(ligne.strip().split(",")[6]),
                        "code_pin": int(ligne.strip().split(",")[7])
                    }
                    clients.append(client)
        return clients

    # Fonction pour ajouter ou mettre à jour une transaction dans le fichier transaction.txt
    @staticmethod
    def ecrire_transaction(transaction):
        """Cette fonction ajoute une transaction dans le fichier transaction.txt"""

        with open("transaction.txt", "a", encoding="UTF-8") as fichier:
            fichier.write(f"{','.join([str(i) for i in transaction.to_dict().values()])}" + "\n")

    # Fonction pour lire toutes les transactions depuis le fichier transaction.txt
    @staticmethod
    def lire_transactions():
        transactions = []
        if os.path.exists("transaction.txt"):
            with open("transaction.txt", "r") as fichier:
                for ligne in fichier:
                    transaction = {
                        "numero_compte": int(ligne.strip().split(",")[0]),
                        "montant": float(ligne.strip().split(",")[1]),
                        "type_transaction": ligne.strip().split(",")[2],
                        "numero_compte_destinataire": int(ligne.strip().split(",")[3]) if ligne.strip().split(",")[3] else None
                    }
                    transactions.append(transaction)
        return transactions










class Transaction():
    
    @staticmethod
    def retrait(client, montant):
        """ Cette fonction permet de retirer un montant du solde d'un client. Elle permet de vérifier le solde juste avant d'essayer
        de faire le retrait, au cas ou le client resoit un dépôt pendant qu'il est connecté. """
        montant = -1*montant
        if not Sauvegarde.ecrire_client(client,montant, True):
            print("Solde insuffisant")
    
    def depot(client, montant):
        Sauvegarde.ecrire_client(client,montant, True)
       

    def virement(client, client_destinataire, montant):
        retrait(client, montant)
        depot(client_destinataire, montant)

    def __str__(self) -> str:
        return f"{self.client.numero_compte} {self.montant} {self.type_transaction} {self.client_destinataire.numero_compte if self.client_destinataire else ''}"

    def to_dict(self):
        """ Transormer en un dictionnaire pour le fichier transaction.txt """
        return {
            "numero_compte": self.client.numero_compte,
            "montant": self.montant,
            "type_transaction": self.type_transaction,
            "numero_compte_destinataire": self.client_destinataire.numero_compte if self.client_destinataire else ''
        }



def numero_compte_to_client(numero_compte: int) -> Client:
    """Cette fonction prend un numéro de compte et retourne le client correspondant"""
    clients = lire_clients()
    for client in clients:
        if client["numero_compte"] == numero_compte:
            client_ = Client()
            client_.from_dict(client)
            return client_



def creer_compte():
    client = Client()
    Choix_type_compte = input("""
    1. Compte courant
    2. Compte épargne
    """)

    while Choix_type_compte not in ["1", "2"]:
        print("Choix invalide")
        Choix_type_compte = input("""
        1. Compte courant
        2. Compte épargne
        """)

    if Choix_type_compte == "1":
        client.type_compte = "courant"

    elif Choix_type_compte == "2":
        type_compte = "epargne"
        faire_depot = input("""Pour créer un compte épargne vous devez d'abord faire un dépôt initial d'au moins 5000 FCFA.
        Voulez-vous faire un dépôt initial maintenant?
        1. Oui
        2. Non""")

        while faire_depot not in ["1", "2"]:
            print("Choix invalide")
            faire_depot = input("""Voulez-vous faire un dépôt initial maintenant?
            1. Oui
            2. Non \n""")
 
        if faire_depot == "1":
            montant = input("Entrez le montant à déposer ou 0 pour annuler: ")
            while not montant.isdigit():
                print("Le montant doit être un nombre entier")
                montant = input("Entrez le montant à déposer: ")
            montant = float(montant)
            if montant < 5000:
                print("Le montant minimum pour un compte épargne est de 5000 FCFA")
            elif montant >= 5000:
                client.solde = montant
                client.type_compte = "epargne"
                print("Compte épargne créé avec succès")
            elif montant == 0:
                print("Création de compte annulée")
                return None
        else:
            print("Création de compte annulée")
            return None

    client.nom = input("Entrez votre nom: ")
    client.prenom = input("Entrez votre prénom: ")
    client.numero_telephone = "".join(input("Entrez votre numéro de téléphone sans indicatif (Vous pouvez séparer les chiffres par des espaces): ").split())

    while len(client.numero_telephone) != 8 or not client.numero_telephone.isdigit():
        print("Le numéro de téléphone doit être composé de 8 chiffres")
        client.numero_telephone = "".join(input("Entrez votre numéro de téléphone (Vous pouvez séparer les chiffres par des espaces): ").split())
    
    client.code_pin = input("Entrez votre code PIN à 4 chiffres: ")

    while len(client.code_pin) != 4 or not client.code_pin.isdigit():
        print("Le code PIN doit être composé de 4 chiffres")
        client.code_pin = input("Entrez votre code PIN à 4 chiffres: ")
    
    Sauvegarde.ecrire_client(client)
    print("Compte créé avec succès !")



def changer_code_pin():
    numero_compte = input("Entrez votre numéro de compte: ")
    while not numero_compte.isdigit():
        print("Le numéro de compte doit être un nombre entier")
        numero_compte = input("Entrez votre numéro de compte: ")
    numero_compte = int(numero_compte)
    client = Sauvegarde.lire_client(numero_compte)
    if not client:
        print("Ce numéro de compte n'existe pas")
        return None
    code_pin = input("Entrez votre code PIN actuel: ")
    while code_pin != client.code_pin:
        print("Code PIN incorrect")
        code_pin = input("Entrez votre code PIN actuel: ")
    nouveau_code_pin = input("Entrez votre nouveau code PIN à 4 chiffres: ")
    nouveau_code_pin_2 = input("Entrez votre nouveau code PIN à 4 chiffres une deuxièmme fois: ")
    while len(nouveau_code_pin) != 4 or not nouveau_code_pin.isdigit() or nouveau_code_pin != nouveau_code_pin_2:
        if nouveau_code_pin != nouveau_code_pin_2:
            print("Les codes PIN ne correspondent pas")
        else:
            print("Le code PIN doit être composé de 4 chiffres")
        nouveau_code_pin = input("Entrez votre nouveau code PIN à 4 chiffres: ")
        nouveau_code_pin_2 = input("Entrez votre nouveau code PIN à 4 chiffres une deuxièmme fois: ")
    
    client.code_pin = nouveau_code_pin
    Sauvegarde.ecrire_client(client)
    print("Code PIN modifié avec succès")


def menu(client_socket):
    # Envoi du menu au client
    menu_text = """
    1. Créer un compte
    2. Se connecter
    3. Changer le code PIN
    4. Quitter
    """
    client_socket.send(menu_text.encode())

    # Réception du choix du client
    choix = client_socket.recv(1024).decode().strip()

    # Vérification du choix
    while choix not in ["1", "2", "3", "4"]:
        client_socket.send("Choix invalide. Veuillez réessayer.\n".encode())
        choix = client_socket.recv(1024).decode().strip()

    # Exécution des actions en fonction du choix
    if choix == "1":
        creer_compte(client_socket)
    elif choix == "2":
        se_connecter(client_socket)
    elif choix == "3":
        changer_code_pin(client_socket)
    elif choix == "4":
        client_socket.send("Merci d'avoir utilisé nos services\n".encode())
        return None



if __name__ == "__main__":
    """client1 = Serveur.Client("Doe", "John", "123456789", "courant", "actif", 1000, 1234)
    client2 = Serveur.Client("Doe", "Jane", "987654321", "epargne", "actif", 5000, 4321)

    # Écrire ou mettre à jour des clients dans le fichier
    ecrire_client(client1)
    ecrire_client(client2)

    # Lire et afficher les clients
    clients = lire_clients()
    # for client in clients:
        # print(client)

    # Créer et écrire une transaction
    transaction = operation.Transaction(1, 200, "retrait")
    transaction.retrait()

    # Lire et afficher les transactions
    transactions = lire_transactions()
    for trans in transactions:
        print(trans)

    #print(client1.to_string_clients())
    """

    print(Sauvegarde.lire_clients)

    creer_compte()