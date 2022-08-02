from datetime import datetime
import json
from socket import *
from sqlite3 import connect
import sys
from threading import Thread 

blockedUsers = {}
loginAttempts = {}

def server(port, numFails) :
    serverPort = port 
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', serverPort))
    serverSocket.listen(1)
    print("Server is on")
    while (True): 
        connectionSocket, addr = serverSocket.accept()
        
                
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket, numFails):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False 
        self.numFails = numFails
        print(" New connection created for: ", clientAddress)
        self.clientAlive = True 
    
    def run(self):
        while self.clientAlive:
            data = self.clientSocket.recv(1024)
            if not data:
                break
            receivedMessage = json.loads(data.decode()) 
            if (receivedMessage['type'] == "login"):
                user = receivedMessage['username']
                pw = receivedMessage['password']
                # if blocked check if 10 seconds has passed and check password
                # otherwise send blocked message 
                if (user in blockedUsers):
                    timeNow = datetime.now()
                    duration = timeNow - blockedUsers[user]
                    if (duration.seconds >= 10):
                        blockedUsers.pop(user)
                    else:
                        self.clientSocket.send(("blocked").encode())
                        continue
                # check if password and username are correct
                # if correct send success message otherwise add user to failed attempts
                for line in open("credentials.txt", "r").readlines():
                    login = line.split()
                    if user == login[0] and pw == login[1]:
                        print("Successfully logged in")
                        message = "success"
                        self.clientSocket.send(message.encode())
                        print("continued")
                        continue
                # if failed before add fail attempt
                if user in loginAttempts: 
                    loginAttempts[user] += 1
                    # if fail attempts exceed numFails add to blocked users and send timeout 
                    if (loginAttempts[user] >= self.numFails):
                        blockedUsers[user] = datetime.now()
                        self.clientSocket.send(("timeout").encode())
                        continue
                # add user has failed an attempt 
                else:
                    loginAttempts[user] = 1
                self.clientSocket.send(("fail").encode())
                
            elif (receivedMessage['type'] == "login"):
                # set address and sequence number make the document for active users 
                print("yep")
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Required server_port and number_of_consecutive_failed_attemps")
        exit()
    serverPort = int(sys.argv[1])
    numFails = int(sys.argv[2])
    if (1 > numFails and numFails > 5):    
        print("Has to be an integer between 1 and 5")
        print(sys.argv[2])
        exit()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', serverPort))
    print("Server is on")
    while True:
        serverSocket.listen()
        connectionSocket, addr = serverSocket.accept()
        clientThread = ClientThread(addr, connectionSocket, numFails)
        clientThread.start()