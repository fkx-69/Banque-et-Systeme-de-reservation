import threading
import socket
import reservation_operation

socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = ''
PORT = 1234

socket.bind((HOST, PORT))

print("Waiting for connection")

while True:
    socket.listen()
    conn, addr = socket.accept()
    thread = threading.Thread(target=reservation_operation.menu, args=(conn,))
    thread.start()
    
    print(f"{addr} connecté")
