import threading
import sauvegarder

class Client:
    
    numero_compte = 1

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
        sauvegarder.ecrire_client(self)
        print(f"Votre compte de numéro {self.numero_compte} a été fermé")

    

if __name__ == "__main__":

    client1 = Client("Doe", "John", "123456789", "courant", "actif", 1000, 1234)
    client2 = Client("Doe", "Jane", "987654321", "epargne", "actif", 5000, 4321)
    client3 = Client()
    client3.from_string(client1.to_string())
    print(client3)

