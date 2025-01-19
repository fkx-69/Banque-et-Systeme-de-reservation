import socket

def client_program():
    # Connexion au serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 1234))

    # Communication avec le serveur
    while True:
        # Réception du menu
        menu = client_socket.recv(1024).decode()
        print(menu)

        # Envoi du choix
        choix = input("Entrez le numéro de l'option choisie: ")
        client_socket.send(choix.encode())

        # Réception de la réponse du serveur
        response = client_socket.recv(1024).decode()
        print(response)

        # Arrêt si l'utilisateur quitte
        if choix == "4":
            break

    # Fermeture du socket
    client_socket.close()

# Lancer le client
client_program()

