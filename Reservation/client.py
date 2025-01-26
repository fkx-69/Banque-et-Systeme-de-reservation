import socket

def client_program():
    # Connexion au serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 1234))

    # Communication avec le serveur
    while True:
        # Réception du message
        message = client_socket.recv(1024).decode()

        if message[-1] == "#":
            print(message.replace("#", ""))
            continue
          
        print(message)

        # Envoi du choix
        choix = input("")
        if choix == '':
            choix = '.'
            
        client_socket.send(choix.encode("utf8"))

        if choix == '0':
            print("Bye !")
            break
        
        # Réception de la réponse du serveur
        #response = client_socket.recv(1024).decode()

    # Fermeture du socket
    client_socket.close()

# Lancer le client
client_program()

