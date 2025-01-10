import os
import Serveur

# Fonction pour ajouter ou mettre à jour un client dans le fichier client.txt
def ecrire_client(client):
    clients = lire_clients()
    client_existant = False

    # Mettre à jour le client si son numéro de compte existe déjà
    for i, client_dictionnaire in enumerate(clients):
        if client_dictionnaire["numero_compte"] == client.numero_compte:
            clients[i] = client.to_string_clients
            client_existant = True
            break

    if not client_existant:
        clients.append(client.to_string_clients())

    # Écriture des clients dans le fichier
    with open("client.txt", "w") as fichier:
        for client_ in clients:
            fichier.write(f"{",".join([str(i) for i in client_.values()])}" + "\n")

# Fonction pour lire tous les clients depuis le fichier client.txt
def lire_clients():
    clients = []
    if os.path.exists("client.txt"):
        with open("client.txt", "r") as fichier:
            for ligne in fichier:
                client = {
                    "numero_compte": ligne.strip().split(",")[0],
                    "nom":  ligne.strip().split(",")[1],
                    "prenom": ligne.strip().split(",")[2],
                    "numero_telephone": ligne.strip().split(",")[3],
                    "type_compte": ligne.strip().split(",")[4],
                    "statut": ligne.strip().split(",")[5],
                    "solde": ligne.strip().split(",")[6],
                    "code_pin": ligne.strip().split(",")[7]
                }
                clients.append(client)
    return clients

# Fonction pour ajouter ou mettre à jour une transaction dans le fichier transaction.txt
def ecrire_transaction(transaction):
    transactions = lire_transactions()
    transaction_existe = False

    # On suppose que chaque transaction est unique, donc pas de mise à jour ici.
    transactions.append(transaction)

    # Écriture des transactions dans le fichier
    with open("transaction.txt", "w") as fichier:
        for t in transactions:
            fichier.write(t.to_string_transaction() + "\n")

# Fonction pour lire toutes les transactions depuis le fichier transaction.txt
def lire_transactions():
    transactions = []
    if os.path.exists("transaction.txt"):
        with open("transaction.txt", "r") as fichier:
            for ligne in fichier:
                transaction = Transaction(None, 0, "")
                transaction.from_string_transaction(ligne.strip())
                transactions.append(transaction)
    return transactions

# Exemple d'utilisation
if __name__ == "__main__":
    client1 = Serveur.Client("Doe", "John", "123456789", "courant", "actif", 1000, 1234)
    client2 = Serveur.Client("Doe", "Jane", "987654321", "epargne", "actif", 5000, 4321)

    # Écrire ou mettre à jour des clients dans le fichier
    ecrire_client(client1)
    ecrire_client(client2)

    # Lire et afficher les clients
    clients = lire_clients()
    # for client in clients:
        # print(client)
    """
    # Créer et écrire une transaction
    transaction = Transaction(client1, 200, "retrait")
    transaction.retrait()
    ecrire_transaction(transaction)

    # Lire et afficher les transactions
    transactions = lire_transactions()
    for trans in transactions:
        print(trans)"""

    #print(client1.to_string_clients())
