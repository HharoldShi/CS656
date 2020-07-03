import time
from socket import *
from packet import *
import threading
import sys


# class Timer(object):
#     def __init__(self):
#         self.start_time = None
#
#     def start(self):
#         self.start_time = time.time()
#
#     def stop(self):
#         self.start_time = None
#
#     def time_elapsed(self):
#         if self.start_time is None:
#             print(0)
#             return 0
#         else:
#             print(time.time()*1000 - self.start_time*1000)
#             # print(self.start_time)
#             return time.time()*1000 - self.start_time*1000 # in milliseconds




base = 0
nextseqnum: int = 0
n = 10  # window size
sndpkt = {}  # dictionary of packet that has been sent
timeout = 100  # ms
# timer = Timer()
udpsocket = socket(AF_INET, SOCK_DGRAM)
mutex = threading.Lock()
restart_timer = False

def udt_send(packet, emulatorIp, emulatorPort):
    udpsocket.sendto(packet.get_udp_data(), (emulatorIp, emulatorPort))


def rdt_send(data, emulatorIp, emulatorPort, timer):
    # create a packet of the data, append the packet into the sndpkt list
    # each packet is associate with a sequence number
    # send the packet through udt
    # restart timer if this packet is the oldest unacknowledged packet
    sndpkt[nextseqnum] = packet.create_packet(nextseqnum, data)
    udt_send(sndpkt[nextseqnum], emulatorIp, emulatorPort)
    if base == nextseqnum:
        print("base == nextseqnum, restart timer")
        timer.start()


def rdt_rcv(senderPort, timer):
    print("rdt_rcv starts. ")
    udpsocket_rcv = socket(AF_INET, SOCK_DGRAM)
    udpsocket_rcv.bind(('', senderPort))
    acklog = open("ack.log", "w")
    while True:
        rcvdata, emulator_adress = udpsocket_rcv.recvfrom(1024)
        rcv_packet = packet.parse_udp_data(rcvdata)
        global base
        if rcv_packet.type == 0 and rcv_packet.seq_num == base:
            acklog.write(str(rcv_packet.seq_num) + '\n')
            base = (rcv_packet.seq_num + 1) % 32
            if base == nextseqnum:
                # timer.stop()
                timer.cancel()
            else:
                timer.cancel()
                timer.start()
        elif rcv_packet.type == 2:
            break
    acklog.close()
    # exit(0)


# def check_timeout(stop_event, emulatorIp, emulatorPort):
#     print("check_timeout stars")
#     while not stop_event.is_set():
#         if timer.start_time is None:
#             continue
#         elif timer.time_elapsed() >= timeout:
#             timer.start()
#             i = base
#             while base <= i < nextseqnum:
#                 udt_send(sndpkt[i],emulatorIp, emulatorPort)
#                 i += 1


# def check_timeout(stop_event, emulatorIp, emulatorPort):
#     while not stop_event.is_set():
#         while restart_timer:
#             time.sleep(0.1)
#             i = base
#             while base <= i < nextseqnum:
#                 udt_send(sndpkt[i],emulatorIp, emulatorPort)
#                 i += 1

def timeout_event(emulatorIp, emulatorPort):
    i = base
    while base <= i < nextseqnum:
        udt_send(sndpkt[i],emulatorIp, emulatorPort)
        i += 1


def main():
    emulatorIp = sys.argv[1]
    emulatorPort = int(sys.argv[2])
    senderPort = int(sys.argv[3])
    file = sys.argv[4]

    timer = threading.Timer(timeout, timeout_event, args=(emulatorIp, emulatorPort))

    # stop_event = threading.Event()
    t1 = threading.Thread(target=rdt_rcv, args=(senderPort,timer))
    # t2 = threading.Thread(target=check_timeout, args=(stop_event,emulatorIp, emulatorPort))
    t1.start()
    # t2.start()

    # read data from file
    seqlog = open("seqnum.log", "w")
    with open(file, "r") as f:
        # read data until EOF
        while True:
            # read data into 500 bytes pieces
            piece = f.read(500)
            # EOF
            if piece == "":
                break
            # keep checking whether the window is not full, and
            # send data only when the window is not full
            while True:
                global nextseqnum
                if nextseqnum < base + n:
                    rdt_send(piece, emulatorIp, emulatorPort, timer)
                    print("send data packet" + str(nextseqnum))
                    seqlog.write(str(nextseqnum) + "\n")
                    nextseqnum += 1
                    nextseqnum = nextseqnum % 32
                    break
    seqlog.close()
    # send EOT to receiver
    udt_send(packet.create_eot(nextseqnum), emulatorIp, emulatorPort)
    print("sender sends eot")
    t1.join()
    print("rdt_rcv stops")
    # stop_event.set()
    # t2.join()
    # print("check_timeout stops")
    exit(0)


if __name__ == '__main__':
    main()
