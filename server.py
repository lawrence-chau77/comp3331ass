import json
from socket import *
import sys 


def server(port, num_fails) :
    serverPort = port 
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', serverPort))
    serverSocket.listen(1)
    print("Server is on")
    while (True):
        connectionSocket, addr = serverSocket.accept()

def respond(connectionSocket):
    while (True):
        # recieve data 
        data = connectionSocket.recv(1024)
        if not data:
            break
        receivedMessage = json.loads(data.decode())
        for line in open("credentials.txt", "r").readlines():
            login = line.split()
            if receivedMessage['username'] == login[0] and receivedMessage['password'] == login[1]:
                print("Successfully logged in")
                message = "success"
                connectionSocket.send(message.encode())
        
    
    
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Required server_port and number_of_consecutive_failed_attemps")
        exit()
    port = int(sys.argv[1])
    if (not isinstance(sys.argv[2], int)):     
        print("Has to be an integer between 1 and 5")
        exit()
    num_fails = int(sys.argv[2])
    server(port, num_fails)