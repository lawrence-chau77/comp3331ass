from datetime import datetime
import json
from socket import *
from sqlite3 import connect
import sys
import os
from threading import Thread 

blockedUsers = {}
loginAttempts = {}
activeUsers = {}

def createFiles():
    f = open("userlog.txt", "w")
    f.close()
    f = open("messagelog.txt", "w")
    f.close()
                
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
            print(receivedMessage)
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
                        message = f'{{"type": "blocked"}}' 
                        self.clientSocket.send((message).encode())
                        continue
                # check if password and username are correct
                # if correct send success message otherwise add user to failed attempts
                elif (user not in blockedUsers):
                    for line in open("credentials.txt", "r").readlines():
                        login = line.split()
                        if user == login[0] and pw == login[1]:
                            message = f'{{"type": "success"}}' 
                            self.clientSocket.send((message).encode())
                            continue
                # if failed before add fail attempt
                elif user in loginAttempts: 
                    loginAttempts[user] += 1
                    # if fail attempts exceed numFails add to blocked users and send timeout 
                    if (loginAttempts[user] >= self.numFails):
                        blockedUsers[user] = datetime.now()
                        message = f'{{"type": "timeout"}}' 
                        self.clientSocket.send((message).encode())
                        continue
                # add user has failed an attempt 
                else:
                    loginAttempts[user] = 1
                    message = f'{{"type": "fail"}}' 
                    self.clientSocket.send((message).encode())
                
            elif (receivedMessage['type'] == "authenticated"):
                # set address and sequence number make the document for active users 
                sequenceNumber = len(activeUsers) + 1
                timestamp = receivedMessage["timestamp"]
                user = receivedMessage["username"]
                addr = self.clientAddress
                udp = receivedMessage["udp"]
                activeUsers[user] = sequenceNumber
                #append
                f = open("userlog.txt", "a")
                f.write(f"{sequenceNumber}; {timestamp}; {user}; {addr[0]}; {udp}")
                f.write("\n")
                f.close()
            
            elif (receivedMessage['type'] == "BCM"):
                f = open("messagelog.txt", "r")
                messageNumber = len(f.readlines()) + 1
                f.close()
                timestamp = receivedMessage["timestamp"]
                user = receivedMessage["username"]
                message = receivedMessage["message"]
                f = open("messagelog.txt", "a")
                f.write(f"{messageNumber}; {timestamp}; {user}; {message}")
                f.write("\n")
                f.close()
                print(f'{user} broadcasted BCM #{messageNumber} "{message}" at {timestamp}')
                message = f'{{"type": "bcm", "messageNumber": "{messageNumber}", "timestamp": "{timestamp}"}}' 
                self.clientSocket.send((message).encode())

            elif (receivedMessage['type'] == "ATU"):
                user = receivedMessage["username"]
                if len(activeUsers) == 1:
                    message = f'{{"type": "empty"}}'
                    self.clientSocket.send((message).encode())
                else:
                    message = f'{{"type": "atu"}}'
                    self.clientSocket.send((message).encode())
                    lines = open("userlog.txt", "r").readlines()
                    # find the last line which isn't the user requesting ATU 
                    for line in lines:
                        login = line.split("; ")
                        if (int(login[0]) != activeUsers[user]):
                            lastLine = line
                            
                    for line in lines:
                        login = line.split("; ")
                        # if last line send last to let client know to stop receiving
                        if (int(login[0]) != activeUsers[user] and (line == lastLine)):
                            message = f'{{"type": "users", "timestamp": "{login[1]}", "username": "{login[2]}", "ip": "{login[3]}", "port": "{login[4][:-1]}", "last": "true"}}'
                            self.clientSocket.send((message).encode())
                            print(f'Return messages: {login[2]}, {login[3]}, {login[4][:-1]}, active since {login[1]}')
                        elif (int(login[0]) != activeUsers[user]):
                            message = f'{{"type": "users", "timestamp": "{login[1]}", "username": "{login[2]}", "ip": "{login[3]}", "port": "{login[4][:-1]}", "last": "false"}}'
                            self.clientSocket.send((message).encode())
                            print(f'Return messages: {login[2]}, {login[3]}, {login[4][:-1]}, active since {login[1]}')

            elif (receivedMessage['type'] == "OUT"):
                #remove user from active users
                user = receivedMessage["username"]
                remove = activeUsers.pop(user)
                #every sequence number higher than number remove 1 
                for k, v in activeUsers.items():
                    if v > remove:
                        activeUsers[k] = (v-1)
                        
                # remove line with user
                with open("userlog.txt", "r") as f:
                    lines = f.readlines()
                with open("userlog.txt", "w") as f:
                    for line in lines:
                        if receivedMessage["username"] not in line:
                            words = line.split("; ")
                            # if seq# higher than user decrement by 1
                            if int(words[0]) > remove:
                                replace = str(int(words[0]) - 1)
                                words[0] = replace
                                line = "; ".join(words)
                            f.write(line)
                                
                message = f'{{"type": "out", "username": "{receivedMessage["username"]}"}}'
                self.clientSocket.send((message).encode())
                print(f'{receivedMessage["username"]} logout')
                
        self.clientSocket.close()

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
    createFiles()
    while True:
        serverSocket.listen()
        connectionSocket, addr = serverSocket.accept()
        clientThread = ClientThread(addr, connectionSocket, numFails)
        clientThread.start()