from socket import *
from pip._vendor.distlib.compat import raw_input

serverName = '172.16.70.199'
serverPort = 12001
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentance = raw_input('Input lowercase sentance')
clientSocket.send(sentance.encode())
modifiedSentance = clientSocket.recv(1024)
print('From server', modifiedSentance.decode())
clientSocket.close()
