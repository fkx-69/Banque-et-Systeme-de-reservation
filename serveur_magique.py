import threading
import socket
from Reservation import reservation_operation
from Banque import operation
import time


socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = ''
PORT = 1234

socket.bind((HOST, PORT))

print("Waiting for connection")

while True:


    socket.listen()
    conn, addr = socket.accept()

    conn.sendall("""Bienvenue sur le Serveur Magique !
    Voulez vous allez vers la:
    1. Banque
    2. Reservation de salle
    """.encode())

    choix_serveur = conn.recv(1024).decode()
    
    while choix_serveur not in ["1", "2"]:
        conn.sendall("Choix invalide. Réessayez: ".encode())
        choix_serveur = conn.recv(1024).decode()
    
    if choix_serveur == "1":
        thread = threading.Thread(target=operation.menu, args=(conn,))
    elif choix_serveur == "2":
        thread = threading.Thread(target=reservation_operation.menu, args=(conn,))
        
    thread.start()
    
    print(f"{addr} connecté")