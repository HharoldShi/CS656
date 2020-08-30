import sys
from socket import *


def main():
    req_code = int(sys.argv[1])
    # array msgList stores messegaes
    msgList = []

    # setup TCP socket for negotiation
    serverTCPSocket = socket(AF_INET, SOCK_STREAM)

    # get a random free port
    serverTCPSocket.bind(('', 0))
    n_port = serverTCPSocket.getsockname()[1]
    print("SERVER_PORT: " + str(n_port))
    f = open('server.txt', 'a')
    f.write("SERVER_PORT: " + str(n_port)+'\n' + '\n')
    f.close()
    serverTCPSocket.listen(1)

    # keeps listening to clients
    while True:
        connectionSocket, address = serverTCPSocket.accept()
        req_code_cli = int(connectionSocket.recv(1024).decode())
        # print("receive req_code_cli = ", req_code_cli)

        # if receiving an invalid req_code, the server sends r_port = 0 to the client
        if req_code != req_code_cli:
            r_port = 0
            connectionSocket.send(str(r_port).encode())
        # receiving a valid req_code
        else:
            # setup UDP connection
            serverUDPSocket = socket(AF_INET, SOCK_DGRAM)
            # get a random free port
            serverUDPSocket.bind(('', 0))
            r_port = serverUDPSocket.getsockname()[1]
            connectionSocket.send(str(r_port).encode())

            # ready to receive messages from the connected client
            while True:
                client_msg, client_address = serverUDPSocket.recvfrom(1024)
                client_msg = client_msg.decode()

                # receive GET message from the client
                if client_msg == "GET":
                    # print("receive message GET")
                    for msg in msgList:
                        serverUDPSocket.sendto(msg.encode(), client_address)
                    serverUDPSocket.sendto("NO MSG".encode(), client_address)

                # receive TERMINATE message from the client
                elif client_msg == "TERMINATE":
                    # print("receive message terminate")
                    serverUDPSocket.close()
                    connectionSocket.close()
                    exit(0)

                # receive a message to store
                else:
                    # print("receive message: " + str(r_port) + ": " + client_msg)
                    msgList.append(str(r_port) + ": " + client_msg)
                    break
            serverUDPSocket.close()
        connectionSocket.close()


if __name__ == '__main__':
    main()
