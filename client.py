from datetime import datetime
from socket import *
import sys

# attemps to authenticate the user
def attemptLogin(clientSocket, udp): 
    username = input("Username: ")
    password = input("Password: ")
    message = f'{{"type": "login", "username": "{username}", "password": "{password}"}}' 
    clientSocket.sendall(message.encode())
    while True:
        data = clientSocket.recv(1024)
        receivedMessage = data.decode()
        # if successful send details and break 
        if receivedMessage == "success":
            print("Welcome to TOOM!")
            timeStamp = datetime.now().strftime("%d %B %Y %H:%M:%S")
            loginDetails = f'{{"type": "login", "timestamp": "{timeStamp}" ,"username": "{username}", "udp": "{udp}"}}' 
            print("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")
            clientSocket.sendall(loginDetails.encode())
            break
        # if fail ask for password again and send to server
        elif receivedMessage == "fail":
            print("Invalid password. Please try again")
            password = input("Password: ")
            clientSocket.sendall(message.encode())
            continue
        # if timeout end terminal
        elif receivedMessage == "timeout":
            print("Invalid pasword. Your account has been blocked. Please try again later")
            break
        # if account blocked end terminal 
        elif receivedMessage == "blocked":
            print("Your account is blocked due to multiple login failures. Please try again later")
            break

def authenticate(ip, port, udpPort) :
    serverAddress = ip 
    serverPort = port 
    clientSocket = socket(AF_INET, SOCK_STREAM)
    serverAddress = (serverAddress, serverPort)
    clientSocket.connect(serverAddress)
    attemptLogin(clientSocket, udpPort)
    # while true:
            
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('required server ip, server port and udp port')
        exit(1)
    ip =  (sys.argv[1])
    port = int (sys.argv[2])
    udpPort = int (sys.argv[3])
    authenticate(ip, port, udpPort)