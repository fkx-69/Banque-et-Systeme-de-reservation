import threading
import read_write
from Serveur import Client

class Transaction():

    def __init__(self, client: Client, montant: float, type_transaction: str, client_destinataire: int = None):
        threading.Thread.__init__(self)
        self.client = client
        self.montant = montant
        self.type_transaction = type_transaction
        self.client_destinataire = client_destinataire # doit etre le client du numero de compte numero_compte_dest

    def retrait(self):
        if self.client.solde >= self.montant:
            self.client.solde -= self.montant
            read_write.ecrire_transaction(self)
            read_write.ecrire_client(self.client)
            return True
        return False    
    
    def depot(self):
        self.client.solde += self.montant
        read_write.ecrire_transaction(self)
        read_write.ecrire_client(self.client)
        return True

    def virement(self):
        if self.client.solde >= self.montant:
            self.client.solde -= self.montant
            self.client_destinataire.solde += self.montant
            read_write.ecrire_transaction(self)
            read_write.ecrire_client(self.client)
            read_write.ecrire_client(self.client_destinataire)
            return True
        return False

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

def Créer_compte():
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

    if Choix == "1":
        client.type_compte = "courant"

    elif Choix == "2":
        type_compte = "epargne"
        faire_depot = input("""Pour créer un compte épargne vous devez d'abord faire un dépôt initial d'au moins 5000 FCFA.
        Voulez-vous faire un dépôt initial maintenant?
        1. Oui
        2. Non""")
        while faire_depot not in ["1", "2"]:
            print("Choix invalide")
            faire_depot = input("""Voulez-vous faire un dépôt initial maintenant?
            1. Oui
            2. Non""")
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
    
    read_write.ecrire_client(client)
    print("Compte créé avec succès !")
    
def changer_code_pin():
    numero_compte = input("Entrez votre numéro de compte: ")
    while not numero_compte.isdigit():
        print("Le numéro de compte doit être un nombre entier")
        numero_compte = input("Entrez votre numéro de compte: ")
    numero_compte = int(numero_compte)
    client = read_write.lire_client(numero_compte)
    if not client:
        print("Ce numéro de compte n'existe pas")
        return None
    code_pin = input("Entrez votre code PIN actuel: ")
    while code_pin != client.code_pin:
        print("Code PIN incorrect")
        code_pin = input("Entrez votre code PIN actuel: ")
    nouveau_code_pin = input("Entrez votre nouveau code PIN à 4 chiffres: ")
    while len(nouveau_code_pin) != 4 or not nouveau_code_pin.isdigit():
        print("Le code PIN doit être composé de 4 chiffres")
        nouveau_code_pin = input("Entrez votre nouveau code PIN à 4 chiffres: ")
    client.code_pin = nouveau_code_pin
    read_write.ecrire_client(client)
    print("Code PIN modifié avec succès")
