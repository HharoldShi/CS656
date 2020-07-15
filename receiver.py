import sys
from packet import *
from socket import *

DEBUG = False


def log(s):
    if DEBUG:
        print(s)


def main():
    emulatorIp = sys.argv[1]
    emulatorPort = int(sys.argv[2])
    receiverPort = int(sys.argv[3])
    fileToWrite = sys.argv[4]

    expseqnum = 0
    ackpkt = packet.create_ack(0)
    is_first_packet_lost = True

    rcvsocket = socket(AF_INET, SOCK_DGRAM)
    rcvsocket.bind(('', receiverPort))

    sndsocket = socket(AF_INET, SOCK_DGRAM)

    f = open(fileToWrite, "w")
    arrivelog = open("arrival.log", "w")
    while True:
        rcvdata, emulatorAddress = rcvsocket.recvfrom(1024)
        rcvpacket = packet.parse_udp_data(rcvdata)

        if rcvpacket.type == 1 and rcvpacket.seq_num != expseqnum:
            if not is_first_packet_lost: # if the first packet is lost, do not send ack
                sndsocket.sendto(ackpkt.get_udp_data(), (emulatorIp, emulatorPort))
            arrivelog.write(str(rcvpacket.seq_num) + '\n')

        elif rcvpacket.type == 1 and rcvpacket.seq_num == expseqnum:
            is_first_packet_lost = False
            ackpkt = packet.create_ack(expseqnum)
            sndsocket.sendto(ackpkt.get_udp_data(), (emulatorIp, emulatorPort))
            f.write(rcvpacket.data)
            arrivelog.write(str(expseqnum) + '\n')
            log("send ack" + str(expseqnum))
            expseqnum += 1
            expseqnum = expseqnum % 32

        elif rcvpacket.type == 2:
            eot_pkt = packet.create_eot(expseqnum)
            sndsocket.sendto(eot_pkt.get_udp_data(), (emulatorIp, emulatorPort))
            log("Receive eot and send eot. ")
            break

    f.close()
    arrivelog.close()
    exit(0)


if __name__ == '__main__':
    main()