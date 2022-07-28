import json
from socket import *
from sqlite3 import connect
import sys 


def server(port, num_fails) :
    serverPort = port 
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('127.0.0.1', serverPort))
    serverSocket.listen(1)
    print("Server is on")
    while (True):
        connectionSocket, addr = serverSocket.accept()
        # recieve data 
        data = connectionSocket.recv(1024)
        if not data:
            break
        receivedMessage = data.decode()
        print(data)
        receivedMessage = json.loads(receivedMessage) 
        if (receivedMessage['type'] == "login"):
            for line in open("credentials.txt", "r").readlines():
                login = line.split()
                if receivedMessage['username'] == login[0] and receivedMessage['password'] == login[1]:
                    print("Successfully logged in")
                    message = "success"
                    connectionSocket.send(message.encode())
            connectionSocket.send(("fail").encode())
        
    
    
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Required server_port and number_of_consecutive_failed_attemps")
        exit()
    port = int(sys.argv[1])
    num_fail = int(sys.argv[2])
    if (1 >= num_fail and num_fail >= 5):    
        print("Has to be an integer between 1 and 5")
        print(sys.argv[2])
        exit()
    num_fails = int(sys.argv[2])
    server(port, num_fails)