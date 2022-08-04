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
            message = f'{{"type": "login", "username": "{username}", "password": "{password}"}}' 
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
            if len(command) == 1:
                print("Error. Message is required for BCM command")
                continue
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
            message = f'{{"type": "ATU", "username": "{username}"}}'
            clientSocket.sendall(message.encode())
            data = clientSocket.recv(1024)
            receivedMessage = json.loads(data.decode())
            print(receivedMessage)
            if receivedMessage["type"] == "empty":
                print("no other active user")
            elif receivedMessage["type"] == "atu":
                data = clientSocket.recv(1024)
                receivedMessage = json.loads(data.decode())
                while(receivedMessage["type"] == "users"):
                    timestamp = receivedMessage["timestamp"]
                    user = receivedMessage["username"]
                    ip = receivedMessage["ip"]
                    port = receivedMessage["port"]
                    print(f'{user}, {ip}, {port}, active since {timestamp}')
                    if receivedMessage["last"] == "true":
                        break
                    data = clientSocket.recv(1024)
                    receivedMessage = json.loads(data.decode())
                    
        elif (command[0] == "SRB"):
            if len(command) == 1:
                print("Error. Usernames are required for SRB command")
                continue
            usernames = commandArgs[commandArgs.index(' ') + 1:]
            message = f'{{"type": "SRB", "username": "{username}", "users": "{usernames}"}}'
            clientSocket.sendall(message.encode())
            data = clientSocket.recv(1024)
            receivedMessage = json.loads(data.decode())
            # if user doesn't exist
            if (receivedMessage["type"] == "invalid"):
                print(f'{receivedMessage["user"]} does not exist')
                continue
            # if user is offline 
            elif (receivedMessage["type"] == "inactive"):
                print(f'{receivedMessage["user"]} is offline')
                continue
            # if user is part of names
            elif (receivedMessage["type"] == "itself"):
                print(f'Cannot include yourself in separate room')
                continue
            # if room already exists
            elif (receivedMessage["type"] == "roomExists"):
                print(f'A separate room (ID: {receivedMessage["id"]}) already created for these users')
                continue
            # successfully created
            elif (receivedMessage["type"] == "srb"):
                print(f'Separate chat room has been created, room ID: {receivedMessage["id"]}, users in this room: {receivedMessage["users"]}')
                
        elif (command[0] == "SRM"):
            if len(command) == 1:
                print("roomID and message is required for SRM command")
            roomId = command[1]
            broadcast = ' '.join(command[2:])
            message = f'{{"type": "SRM", "id": "{roomId}", "username": "{username}", "message": "{broadcast}"}}'
            clientSocket.sendall(message.encode())
            data = clientSocket.recv(1024)
            receivedMessage = json.loads(data.decode())
            # if room id doesn't exist
            if (receivedMessage["type"] == "invalidRoom"):
                print("The separate room does not exist")
                continue
            elif (receivedMessage["type"] == "invalidMember"):
                print("You are not in this separate room chat")
                continue
            
        elif (command[0] == "RDM"):
            print("RDM")
        elif (command[0] == "OUT"):
            message = f'{{"type": "OUT", "username": "{username}"}}'
            clientSocket.sendall((message).encode())
            data = clientSocket.recv(1024)
            receivedMessage = json.loads(data.decode())
            if receivedMessage["type"] == "out":
                print(f'Bye, {receivedMessage["username"]}')
            break
        else:
            print("Error. Invalid command!")
        