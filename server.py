from datetime import datetime
import json
from socket import *
from sqlite3 import connect
import sys 

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
        while (True):
            # recieve data 
            data = connectionSocket.recv(1024)
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
                        connectionSocket.send(("blocked").encode())
                        continue
                # check if password and username are correct
                # if correct send success message otherwise add user to failed attempts
                for line in open("credentials.txt", "r").readlines():
                    login = line.split()
                    if user == login[0] and pw == login[1]:
                        print("Successfully logged in")
                        message = "success"
                        connectionSocket.send(message.encode())
                        print("continued")
                        continue
                # if failed before add fail attempt
                if user in loginAttempts: 
                    loginAttempts[user] += 1
                    # if fail attempts exceed numFails add to blocked users and send timeout 
                    if (loginAttempts[user] >= numFails):
                        blockedUsers[user] = datetime.now()
                        connectionSocket.send(("timeout").encode())
                        continue
                # add user has failed an attempt 
                else:
                    loginAttempts[user] = 1
                connectionSocket.send(("fail").encode())
                
            elif (receivedMessage['type'] == "login"):
                # set address and sequence number make the document for active users 
                print("yep")
                
            
        
    
    
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