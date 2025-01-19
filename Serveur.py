import threading
import socket
import operation

socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = ''
PORT = 1234

socket.bind((HOST, PORT))

while True:
    socket.listen()
    print("Waiting for connection")
    conn, addr = socket.accept()
    operation.menu(conn)



if __name__ == "__main__":

    client1 = Client("Doe", "John", "123456789", "courant", "actif", 1000, 1234)
    client2 = Client("Doe", "Jane", "987654321", "epargne", "actif", 5000, 4321)
    client3 = Client()
    client3.from_string(client1.to_string())
    print(client3)

