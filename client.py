from datetime import datetime
from http import client
import json
from socket import *
import sys

# attemps to authenticate the user
def attemptLogin(username, password, clientSocket, udp): 
    message = f'{{"type": "login", "username": "{username}", "password": "{password}"}}' 
    clientSocket.sendall(message.encode())
    while True:
        data = clientSocket.recv(1024)
        receivedMessage = json.loads(data.decode()) 
        # if successful send details and break 
        if receivedMessage['type'] == "success":
            print("Welcome to TOOM!")
            timeStamp = datetime.now().strftime("%d %B %Y %H:%M:%S")
            loginDetails = f'{{"type": "authenticated", "timestamp": "{timeStamp}" ,"username": "{username}", "udp": "{udp}"}}' 
            clientSocket.sendall(loginDetails.encode())
            break
        # if fail ask for password again and send to server
        elif receivedMessage['type'] == "fail":
            print("Invalid password. Please try again")
            password = input("Password: ")
            clientSocket.sendall(message.encode())
            continue
        # if timeout end terminal
        elif receivedMessage['type'] == "timeout":
            print("Invalid pasword. Your account has been blocked. Please try again later")
            quit()
        # if account blocked end terminal 
        elif receivedMessage['type'] == "blocked":
            print("Your account is blocked due to multiple login failures. Please try again later")
            quit()
            
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('required server ip, server port and udp port')
        exit(1)
    serverAddress =  (sys.argv[1])
    serverPort = int (sys.argv[2])
    udpPort = int (sys.argv[3])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    serverAddress = (serverAddress, serverPort)
    clientSocket.connect(serverAddress)
    username = input("Username: ")
    password = input("Password: ")
    attemptLogin(username, password, clientSocket, udpPort)
    while True:
        commandArgs = input("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT) : ")
        command = commandArgs.split()
        if (command[0] == "BCM"):
            broadcast = commandArgs[commandArgs.index(' ') + 1:]
            timeStamp = datetime.now().strftime("%d %B %Y %H:%M:%S")
            message = f'{{"type": "BCM", "timestamp": "{timeStamp}", "username": "{username}", "message": "{broadcast}"}}' 
            clientSocket.sendall(message.encode())
            data = clientSocket.recv(1024)
            receivedMessage = json.loads(data.decode())
            if receivedMessage["type"] == "bcm":
                messageNumber = receivedMessage["messageNumber"]
                timestamp = receivedMessage["timestamp"]
                print(f"Broadcast message, #{messageNumber} broadcast at {timestamp}")
                continue
        elif (command[0] == "ATU"):
            message = f'{{"type": "ATU", "username": "{username}}}'
            clientSocket.sendall(message.encode())
            data = clientSocket.recv(1024)
            receivedMessage = json.loads(data.decode())
            if receivedMessage["type"] == "empty":
                print("no other active user")
            elif receivedMessage["ty[e"] == "users":
                print(data)
                print(receivedMessage)
        elif (command[0] == "SRB"):
            print("SRB")
        elif (command[0] == "SRM"):
            print("SRM")
        elif (command[0] == "RDM"):
            print("RDM")
        elif (command[0] == "OUT"):
            print("OUT")
        