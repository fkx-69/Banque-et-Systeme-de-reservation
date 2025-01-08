import threading

class Client:
    
    numero_compte = 0

    def __init__(self):
        self.nom = ""
        self.prenom = ""
        self.numero_telephone = ""
        self.type_compte = ""
        self.statut = "actif"
        self.solde = 0
        self.code_pin = 0
        self.numero_compte = Client.numero_compte
        Client.numero_compte += 1

    def __str__(self):
        return f"{self.numero_compte} {self.nom} {self.prenom} {self.numero_telephone} {self.type_compte} {self.statut} {self.solde}"
    
    def to_string_clients(self):
        # Transormer en une ligne de texte pour le ficiher client.txt
        return f"{self.numero_compte},{self.nom},{self.prenom},{self.numero_telephone},{self.type_compte},{self.statut},{self.solde},{self.code_pin}"

    def from_string_client(self, ligne):
        # Transformer une ligne de texte en objet Client
        self.numero_compte, self.nom, self.prenom, self.numero_telephone, self.type_compte, self.statut, self.solde = ligne.split(',')
        self.numero_compte = int(self.numero_compte)
        self.solde = float(self.solde)
        self.code_pin = int(self.code_pin)


class Transaction(threading.Thread):

    def __init__(self, client: Client, montant: float, type_transaction: str, client_destinataire: Client = None):
        threading.Thread.__init__(self)
        self.client = client
        self.montant = montant
        self.type_transaction = type_transaction
        self.client_destinataire = client_destinataire

    def retrait(self):
        if self.client.solde >= self.montant:
            self.client.solde -= self.montant
            return True
        return False    
    
    def depot(self):
        self.client.solde += self.montant
        return True

    def virement(self):
        if self.client.solde >= self.montant:
            self.client.solde -= self.montant
            self.client_destinataire.solde += self.montant
            return True
        return False

    def __str__(self) -> str:
        return f"{self.client.numero_compte} {self.montant} {self.type_transaction} {self.client_destinataire.numero_compte if self.client_destinataire else ''}"

    def to_string_transaction(self):
        return f"{self.client.numero_compte},{self.montant},{self.type_transaction},{self.client_destinataire.numero_compte if self.client_destinataire else ''}"

    def from_string_transaction(self, ligne):
        self.client.numero_compte, self.montant, self.type_transaction, numero_compte_destinataire = ligne.split(',')
        self.client.numero_compte = int(self.client.numero_compte)
        self.montant = float(self.montant)
        self.client_destinataire = Client() # a revoir
        self.client_destinataire.numero_compte = int(numero_compte_destinataire) # a revoir