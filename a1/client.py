import sys
from socket import *


def main():
    server_address = sys.argv[1]
    n_port = int(sys.argv[2])
    req_code = int(sys.argv[3])
    msg = sys.argv[4]
    # set TCP connection to server
    TCPSocket = socket(AF_INET, SOCK_STREAM)
    try:
        TCPSocket.connect((server_address, n_port))
    except ConnectionRefusedError as err:
        sys.stderr.write("Error server_unavailable" + '\n')
        f = open('client.txt', 'a')
        f.write("Error server_unavailable" + '\n')
        f.write('\n')
        exit(1)
    # send req_code and check returned r_port
    TCPSocket.send(str(req_code).encode())
    r_port = int(TCPSocket.recv(1024).decode())
    if r_port == 0:
        sys.stderr.write("Invalid req_code.\n")
        f = open('client.txt', 'a')
        f.write('r_port: ' + str(r_port) + '\n')
        f.write("Invalid req_code. \n")
        f.write('\n')
        TCPSocket.close()
        sys.exit(1)
    else:
        TCPSocket.close()

    # setup UDP connection to server
    UDPSocket = socket(AF_INET, SOCK_DGRAM)

    # send GET to server and print all messages
    UDPSocket.sendto("GET".encode(), (server_address, r_port))
    received_msg = ""
    f = open('client.txt', 'a')
    f.write('r_port: ' + str(r_port) + '\n')
    while received_msg != "NO MSG":
        received_msg, serverAddress = UDPSocket.recvfrom(1024)
        received_msg = received_msg.decode()
        print(received_msg)
        # if received_msg != "NO MSG":
        f.write(received_msg + '\n')
    f.write('\n')
    f.close()

    # send message to be stored at the server
    UDPSocket.sendto(msg.encode(), (server_address, r_port))

    # close UDP socket and exit client
    UDPSocket.close()
    print("Press enter to exit. ")
    input = sys.stdin.readline()
    if input != None:
        exit(0)


if __name__ == '__main__':
    main()
