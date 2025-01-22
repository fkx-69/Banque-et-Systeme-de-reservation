import threading
import socket
from operation import *

socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = ''
PORT = 1234

socket.bind((HOST, PORT))

while True:
    socket.listen()
    print("Waiting for connection")
    conn, addr = socket.accept()
    thread = threading.Thread(target=menu, args=(conn,))

    thread.start()