import os
from datetime import datetime
import threading

FICHIER_CLIENT = "client.txt"
FICHIER_TRANSACTION = "transaction.txt"

def lire_client():
    if not os.path.exists(FICHIER_CLIENT):
        return  []

    with open("nom_fichier.txt", "r") as fichier:
        clients = []
        for line in fichier.readlines():
            num_compte, nom, prenom, numero_telephone, type_compte, statut, solde, code_pin = line.strip().split(" : ")
            clients.append({
                "num_compte": num_compte,
                "nom": nom,
                "prenom": prenom,
                "numero_telephone": numero_telephone,
                "type_compte": type_compte,
                "statut": statut,
                "solde": int(solde),
                "code_pin": code_pin
            })
        return clients
    
def ecrire_client(client):
    clients = lire_clients()
    for i, c in enumerate(clients):
        if c.numero_compte == client.numero_compte:
            clients[i] = client
            break
    else:
        clients.append(client)
    with open(FICHIER_CLIENTS, "w") as fichier:
        for c in clients:
            fichier.write(c.to_string_clients() + "\n")

def lire_transactions():
    transactions = []
    if not os.path.exists(FICHIER_TRANSACTIONS):
        return transactions
    with open(FICHIER_TRANSACTIONS, "r") as fichier:
        for ligne in fichier:
            transaction = Transaction(client=None, montant=0, type_transaction="")
            transaction.from_string_transaction(ligne.strip())
            transactions.append(transaction)
    return transactions

def ecrire_transaction(transaction):
    with open(FICHIER_TRANSACTIONS, "a") as fichier:
        fichier.write(transaction.to_string_transaction() + "\n")

