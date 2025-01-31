import threading
import socket
import os
import time
import random

#### rappel: ajouter une fonction pour verifier le status des compte avant opération

class Client:
    
    numero_compte = random.randint(100_000, 999_999)

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



#-----------------------------------------------------------------------------------------------------



class Sauvegarde: 

    lock = threading.Lock()

    # Fonction pour ajouter ou mettre à jour un client dans le fichier client.txt
    @staticmethod
    def ecrire_client(client: Client, montant: float = 0) -> None:
        """Cette fonction ajoute ou met à jour un client dans le fichier client.txt"""
        with Sauvegarde.lock:
            
            clients = Sauvegarde.lire_clients()
            client_existe = False
            # Écriture des clients dans le fichier
            with open("client.txt", "w", encoding="UTF-8") as fichier:
                

                # Mettre à jour le client si son numéro de compte existe déjà
                for i, client_dictionnaire in enumerate(clients):
                    if client_dictionnaire["numero_compte"] == client.numero_compte:
                        
                        if montant != 0 and client_dictionnaire["solde"] + montant < 0: 
                            if client_dictionnaire["type_compte"] == "epargne" and client_dictionnaire["solde"] + montant < 5000:                   
                                return "Solde insufisant"
                        else:
                            clients[i]["solde"] += montant


                        if client_dictionnaire["code_pin"] != client.code_pin:
                            clients[i]["code_pin"] = client.code_pin

                        if client_dictionnaire["statut"] != client.statut:
                            clients[i]["statut"] = client.statut
                            

                        client_existe = True
                        break

                if not client_existe:
                    clients.append(client.to_dict())

                for client_ in clients:
                    fichier.write(f"{','.join([str(i) for i in client_.values()])}" + "\n")
                return True


    # Fonction pour lire tous les clients depuis le fichier client.txt
    @staticmethod
    def lire_clients() -> list:
        """Cette fonction lit les clients depuis le fichier client.txt et les retourne sous forme de liste de dictionnaires"""
        clients = []
        if os.path.exists("client.txt"):
            with open("client.txt", "r", encoding="UTF-8") as fichier:
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
            fichier.write(f"{','.join([str(i) for i in transaction.values()])}" + "\n")

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



#-----------------------------------------------------------------------------------------------------



class Transaction():
    
    @staticmethod
    def retrait(client, montant):
        """ Cette fonction permet de retirer un montant du solde d'un client. Elle permet de vérifier le solde juste avant d'essayer
        de faire le retrait, au cas ou le client resoit un dépôt pendant qu'il est connecté. """
        montant = -1*montant
        if not Sauvegarde.ecrire_client(client,montant):
            return("Solde insuffisant") ## a changer pour un message d'erreur au client
        Sauvegarde.ecrire_transaction(Transaction.to_dict("retrait", montant, client))
    
    def depot(client, montant):
        Sauvegarde.ecrire_client(client,montant)
        Sauvegarde.ecrire_transaction(Transaction.to_dict("depot", montant, client_destinataire= client))
       

    def virement(client, client_destinataire, montant):
        Transaction.retrait(client, montant)
        Transaction.depot(client_destinataire, montant)
        Sauvegarde.ecrire_transaction(Transaction.to_dict("virement", montant, client, client_destinataire))


    @staticmethod
    def to_dict(type_transaction: str, montant: float, client_source: Client = None, client_destinataire: Client = None) -> dict:
        """ Transormer en un dictionnaire pour le fichier transaction.txt """
        return {
            "type_transaction": type_transaction,
            "montant": montant,
            "numero_compte": client_source.numero_compte if client_source else '',
            "numero_compte_destinataire": client_destinataire.numero_compte if client_destinataire else ''
        }




#-----------------------------------------------------------------------------------------------------

def numero_compte_to_client(numero_compte: int) -> Client:
    """Cette fonction prend un numéro de compte et retourne le client correspondant"""
    clients = Sauvegarde.lire_clients()
    for client in clients:
        if client["numero_compte"] == numero_compte:
            client_ = Client()
            client_.from_dict(client)
            return client_


def menu(client_socket):
    # Envoi du menu au client
    menu_text = """
    1. Créer un compte
    2. Faire une transaction
    3. Changer le code PIN
    4. Fermer votre compte
    5. Consulter votre compte
    0. Quitter
    """
    client_socket.send(menu_text.encode())

    # Réception du choix du client
    choix = client_socket.recv(1024).decode().strip()

    # Vérification du choix
    while not choix in ["0","1", "2", "3", "4", "5"]:
        client_socket.send("Choix invalide. Veuillez réessayer.\n".encode())
        choix = client_socket.recv(1024).decode().strip()

    # Exécution des actions en fonction du choix
    if choix == "1":
        creer_compte(client_socket)
    elif choix == "2":
        menu_transaction(client_socket)
    elif choix == "3":
        changer_code_pin(client_socket)
    elif choix == "4":
        fermer_compte(client_socket)
    elif choix == "5":
        consulter_compte(client_socket)
    elif choix == "0":
        client_socket.send("Merci d'avoir utilisé nos services\n".encode())
        return None


def menu_transaction(client_socket):
    # Envoi du menu au client
    menu_text = """
    1. Faire un dépôt
    2. Faire un retrait
    3. Faire un virement
    4. Retour
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
        faire_depot(client_socket)
    elif choix == "2":
        faire_retrait(client_socket)
    elif choix == "3":
        faire_virement(client_socket)
    elif choix == "4":
        menu(client_socket)

def demander_numero_compte(client_socket, is_destinataire=False):
    message = "Entrez le numéro de compte du destinataire: " if is_destinataire else "Entrez votre numéro de compte: "
    client_socket.send(message.encode())
    numero_compte = client_socket.recv(1024).decode().strip()
    while not numero_compte.isdigit():
        client_socket.send("Le numéro de compte doit être un nombre entier. Réessayez: ".encode())
        numero_compte = client_socket.recv(1024).decode().strip()
    return int(numero_compte)

def demander_code_pin(client_socket):
    client_socket.send("Entrez votre code PIN: ".encode())
    code_pin = client_socket.recv(1024).decode().strip()
    while len(code_pin) != 4 or not code_pin.isdigit():
        client_socket.send("Le code PIN doit être composé de 4 chiffres. Réessayez: ".encode())
        code_pin = client_socket.recv(1024).decode().strip()
    return code_pin

def demander_montant(client_socket):
    client_socket.send("Entrez le montant: ".encode())
    montant = client_socket.recv(1024).decode().strip()
    while not montant.isdigit():
        client_socket.send("Le montant doit être un nombre entier. Réessayez: ".encode())
        montant = client_socket.recv(1024).decode().strip()
    return float(montant)

def faire_depot(client_socket):
    
    numero_compte = demander_numero_compte(client_socket, is_destinataire=True)

    # Lire les informations du client
    client = numero_compte_to_client(numero_compte)
    if not client:
        client_socket.send("Le numéro de compte du destinataire n'existe pas.\n".encode())
        return None
    
    montant = demander_montant(client_socket)

    # Faire le dépôt
    Transaction.depot(client, montant)
    client_socket.send("Dépôt effectué avec succès.\n".encode())
    time.sleep(3)
    menu_transaction(client_socket)


def faire_retrait(client_socket):
    try:
        numero_compte = demander_numero_compte(client_socket)
        client = numero_compte_to_client(numero_compte)
        # Demander le code PIN
        code_pin = int(demander_code_pin(client_socket))

        if not client or client.code_pin != code_pin:
            client_socket.send("Numero de compte ou code PIN incorrect\n#".encode())
            time.sleep(3)
            menu_transaction(client_socket)


        # Demander le montant à retirer
        montant = demander_montant(client_socket)

        # Faire le retrait
        Transaction.retrait(client, montant)
        client_socket.send("Retrait effectué avec succès.\n".encode())
        time.sleep(3)
        menu_transaction(client_socket)
    except Exception as e:
        client_socket.send(f"Une erreur est survenue : {e}\n".encode())

def faire_virement(client_socket):
    try:
        numero_compte = demander_numero_compte(client_socket)
        client = numero_compte_to_client(numero_compte)
        code_pin = int(demander_code_pin(client_socket))


        # Vérifier le code PIN
        if client.code_pin != code_pin or not client:
            client_socket.send("Code PIN incorrect.\n".encode())
            menu_transaction(client_socket)

        numero_compte_destinataire = demander_numero_compte(client_socket, is_destinataire=True)
        client_destinataire = numero_compte_to_client(numero_compte_destinataire)

        if not client_destinataire:
            client_socket.send("Le numéro de compte du destinataire n'existe pas.\n".encode())
            menu_transaction(client_socket)
        
    
        # Demander le montant à transférer
        montant = demander_montant(client_socket)
        Transaction.virement(client, client_destinataire, montant)

        client_socket.send("Virement effectué avec succès.\n".encode())
        time.sleep(3)
        menu_transaction(client_socket)

    except Exception as e:
        client_socket.send(f"Une erreur est survenue : {e}\n".encode())


def creer_compte(client_socket):
    # Création d'une instance de client
    client = Client()
    # Demander le type de compte
    choix_menu = """
    1. Compte courant
    2. Compte épargne
    """
    client_socket.send(choix_menu.encode())
    choix_type_compte = client_socket.recv(1024).decode().strip()

    while choix_type_compte not in ["1", "2"]:
        client_socket.send("Choix invalide. Réessayez.\n".encode())
        choix_type_compte = client_socket.recv(1024).decode().strip()

    if choix_type_compte == "1":
        client.type_compte = "courant"

    elif choix_type_compte == "2":
        type_compte = "epargne"
        demande_depot = """Pour créer un compte épargne, vous devez d'abord faire un dépôt initial d'au moins 5000 FCFA.
        Voulez-vous faire un dépôt initial maintenant ?
        1. Oui
        2. Non
        """
        client_socket.send(demande_depot.encode())
        faire_depot = client_socket.recv(1024).decode().strip()

        while faire_depot not in ["1", "2"]:
            client_socket.send("Choix invalide. Réessayez.\n".encode())
            faire_depot = client_socket.recv(1024).decode().strip()

        if faire_depot == "1":
            client_socket.send("Entrez le montant à déposer ou 0 pour annuler: ".encode())
            montant = client_socket.recv(1024).decode().strip()
            while not montant.isdigit():
                client_socket.send("Le montant doit être un nombre entier. Réessayez: ".encode())
                montant = client_socket.recv(1024).decode().strip()
            montant = float(montant)
            if montant < 5000:
                client_socket.send("Le montant minimum pour un compte épargne est de 5000 FCFA. Opération annulée.\n".encode())
                return None
            elif montant >= 5000:
                client.solde = montant
                client.type_compte = "epargne"
                client_socket.send("Dépot effectué avec succès.\n#".encode())
            elif montant == 0:
                client_socket.send("Création de compte annulée.\n#".encode())
                return None
        else:
            client_socket.send("Création de compte annulée.\n#".encode())
            return None

    time.sleep(1)


    # Demander les informations personnelles
    while True:
        client_socket.send("Entrez votre nom: ".encode())
        client.nom = client_socket.recv(1024).decode().strip()
        if not client.nom.isalpha():
            client_socket.send("Le nom doit contenir seulement deslettres. Réessayez: ".encode())
            time.sleep(1)
            continue
        break
    
    while True:
        client_socket.send("Entrez votre prénom: ".encode())
        client.prenom = client_socket.recv(1024).decode().strip()
        if not client.prenom.isalpha():
            client_socket.send("Le prénom doit contenir seulement deslettres. Réessayez: ".encode())        
            time.sleep(1)
            continue
        break

    client_socket.send("Entrez votre numéro de téléphone (8 chiffres espaces): ".encode())
    client.numero_telephone = "".join(client_socket.recv(1024).decode().strip().split())

    while len(client.numero_telephone) != 8 or not client.numero_telephone.isdigit():
        client_socket.send("Le numéro de téléphone doit être composé de 8 chiffres. Réessayez: ".encode())
        client.numero_telephone = client_socket.recv(1024).decode().strip()

    client_socket.send("Entrez votre code PIN à 4 chiffres: ".encode())
    client.code_pin = client_socket.recv(1024).decode().strip()

    while len(client.code_pin) != 4 or not client.code_pin.isdigit():
        client_socket.send("Le code PIN doit être composé de 4 chiffres. Réessayez: ".encode())
        client.code_pin = client_socket.recv(1024).decode().strip()

    # Sauvegarde des données du client
    Sauvegarde.ecrire_client(client)
    client_socket.send("Compte créé avec succès !\n".encode())
    time.sleep(3)
    menu(client_socket)
    


def changer_code_pin(client_socket):
    try:
        numero_compte = demander_numero_compte(client_socket)
        

        # Lire les informations du client
        client = numero_compte_to_client(numero_compte)
        if not client:
            client_socket.send("Ce numéro de compte n'existe pas.\n".encode())
            return None

        # Demander le code PIN actuel
        client_socket.send("Entrez votre code PIN actuel: ".encode())
        code_pin = int(client_socket.recv(1024).decode().strip())
        while code_pin != client.code_pin:
            client_socket.send("Code PIN incorrect. Réessayez: ".encode())
            code_pin = client_socket.recv(1024).decode().strip()

        # Demander le nouveau code PIN
        client_socket.send("Entrez votre nouveau code PIN à 4 chiffres: ".encode())
        nouveau_code_pin = client_socket.recv(1024).decode().strip()
        client_socket.send("Entrez votre nouveau code PIN à 4 chiffres une deuxième fois: ".encode())
        nouveau_code_pin_2 = client_socket.recv(1024).decode().strip()

        while len(nouveau_code_pin) != 4 or not nouveau_code_pin.isdigit() or nouveau_code_pin != nouveau_code_pin_2:
            client_socket.send("""Le code PIN doit être composé de 4 chiffres. Réessayez.\n
            Entrez votre nouveau code PIN à 4 chiffres:  """.encode())
            nouveau_code_pin = client_socket.recv(1024).decode().strip()
            client_socket.send("Entrez votre nouveau code PIN à 4 chiffres une deuxième fois: ".encode())
            nouveau_code_pin_2 = client_socket.recv(1024).decode().strip()

        # Mise à jour du code PIN
        client.code_pin = nouveau_code_pin
        Sauvegarde.ecrire_client(client)
        client_socket.send("Code PIN modifié avec succès.\n".encode())
        time.sleep(0.1)
        menu(client_socket)
        
    except Exception as e:
        client_socket.send(f"Une erreur est survenue : {e}\n".encode())



def fermer_compte(client_socket):
    try:
        numero_compte = demander_numero_compte(client_socket)
        client = numero_compte_to_client(numero_compte)
        if not client:
            client_socket.send("Ce numéro de compte n'existe pas.\n".encode())
            menu(client_socket)

        # Demander le code PIN
        code_pin = int(demander_code_pin(client_socket))
        # Fermer le compte
        if code_pin == client.code_pin:
            if client.type_compte == "courant" and client.solde > 0:
               
                client_socket.send("Le compte doit avoir un solde de 0 pour pouvoir le fermer.\n".encode())
                time.sleep(0.1)
                menu(client_socket)

            client.statut = "fermé"
            Sauvegarde.ecrire_client(client)
            client_socket.send("Compte fermé avec succès.\n".encode())
            time.sleep(0.1)
            menu(client_socket)
        else:
            client_socket.send("Code PIN incorrect. Compte non fermé.\n".encode())
            time.sleep(0.1)
            menu(client_socket)

    except Exception as e:
        client_socket.send(f"Une erreur est survenue : {e}\n".encode())


def consulter_compte(client_socket):
    try:
        numero_compte = demander_numero_compte(client_socket)
        client = numero_compte_to_client(numero_compte)
        code_pin = int(demander_code_pin(client_socket))
        

        if not client:
            client_socket.send("Ce numéro de compte n'existe pas.\n".encode())
            menu(client_socket)

        if code_pin == client.code_pin:

            # Envoyer les informations du compte au client
            informations_compte = f"""
            Informations du compte:
            -----------------------
            Numéro de compte : {client.numero_compte}
            Nom              : {client.nom}
            Prénom           : {client.prenom}
            Téléphone        : {client.numero_telephone}
            Type de compte   : {client.type_compte}
            Statut           : {client.statut}
            Solde            : {client.solde} FCFA
            """
            client_socket.send(informations_compte.encode())

        else:
            client_socket.send("Code PIN incorrect ou mot de passe incorrect.\n".encode())
        time.sleep(0.1)
        menu(client_socket)
    except Exception as e:
        client_socket.send(f"Une erreur est survenue : {e}\n".encode())

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