import json
from socket import *
import sys
def attemptLogin(clientSocket): 
    username = input("Username: ")
    password = input("Password: ")
    message = f'{{"type": "login", "username": "{username}", "password": "{password}"}}' 
    clientSocket.sendall(message.encode())
    while True:
        data = clientSocket.recv(1024)
        receivedMessage = data.decode()
        if receivedMessage == "success":
            print("Welcome to TOOM!")
            break
        elif receivedMessage == "fail":
            print("invalid password")
            attemptLogin(clientSocket)

def authenticate(ip, port) :
    serverAddress = ip 
    serverPort = port 
    clientSocket = socket(AF_INET, SOCK_STREAM)
    serverAddress = (serverAddress, serverPort)
    clientSocket.connect(serverAddress)
    attemptLogin(clientSocket)
    
            
            
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('required server ip, server port and udp port')
        exit(1)
    ip =  (sys.argv[1])
    port = int (sys.argv[2])
    udp_port = int (sys.argv[3])
    authenticate(ip, port)