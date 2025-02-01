import threading
import socket
from Reservation import reservation_operation
from Banque import operation
import time


socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '192.168.0.102'
PORT = 1234

socket.bind((HOST, PORT))

print("Waiting for connection")

def menu_magique(client_socket):
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
        operation.menu(client_socket)
    elif choix_serveur == "2":
        reservation_operation.menu(client_socket)

while True:


    socket.listen()
    conn, addr = socket.accept()

    thread = threading.Thread(target=menu_magique, args=(conn,))
        
    thread.start()
    
    print(f"{addr} connecté")