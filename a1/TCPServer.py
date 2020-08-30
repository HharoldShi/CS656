from socket import *

serverPort = 12001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
while True:
    connectionSocket, address = serverSocket.accept()
    sentance = connectionSocket.recv(1024).decode()
    modifiedSentance = sentance.upper()
    connectionSocket.send(modifiedSentance.encode())
    connectionSocket.close()