import threading

class Client:
    
    numero_compte = 1

    def __init__(self, nom: str = "", prenom: str = "", numero_telephone: str = "", type_compte: str = "", statut: str = "actif", solde: float = 0, code_pin: int = 0):
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
    
    def to_string(self):
        # Transormer en une ligne de texte pour le ficiher client.txt
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

    def from_string(self, ligne):
        # Transformer une ligne de texte en objet Client
        self.numero_compte, self.nom, self.prenom, self.numero_telephone, self.type_compte, self.statut, self.solde, self.code_pin = [str(i) for i in ligne.values()]


class Transaction(threading.Thread):

    def __init__(self, client: Client, montant: float, type_transaction: str, numero_compte_destinataire: int = None):
        threading.Thread.__init__(self)
        self.client = client
        self.montant = montant
        self.type_transaction = type_transaction
        self.client_destinataire = client_destinataire # doit etre le client du numero de compte numero_compte_dest

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

    def to_string(self):
        return {
            "numero_compte": self.client.numero_compte,
            "montant": self.montant,
            "type_transaction": self.type_transaction,
            "numero_compte_destinataire": self.client_destinataire.numero_compte if self.client_destinataire else ''
        }
    def from_string(self, ligne):
        self.client.numero_compte, self.montant, self.type_transaction, numero_compte_destinataire = [str(i) for i in ligne.values()]

if __name__ == "__main__":

    client1 = Client("Doe", "John", "123456789", "courant", "actif", 1000, 1234)
    client2 = Client("Doe", "Jane", "987654321", "epargne", "actif", 5000, 4321)
    client3 = Client()
    client3.from_string(client1.to_string())
    print(client3)