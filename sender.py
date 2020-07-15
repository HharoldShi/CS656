import time
from socket import *
from packet import *
import threading
import sys

mutex = threading.Lock()


class Timer(object):
    def __init__(self):
        self.start_time = None

    def start(self):
        mutex.acquire()
        try:
            self.start_time = time.monotonic()
        finally:
            mutex.release()

    def stop(self):
        mutex.acquire()
        try:
            self.start_time = None
        finally:
            mutex.release()

    def time_elapsed(self):
        mutex.acquire()
        try:
            if self.start_time is None:  # when a timer stops, the time_elapsed is set to 0.
                return 0
            else:
                return time.monotonic() * 1000 - self.start_time * 1000  # *1000 to convert time to milliseconds
        finally:
            mutex.release()


# Global variables
n = 10  # window size
MAX_DATA_SIZE = packet.MAX_DATA_LENGTH
timeout = 100  # ms

base = 0
nextseqnum: int = 0
num_sent_packets = -1  # number of packets have been sent
num_ack_packets = 0  # number of acknowledgement packets have been received
send_eot_flag = 0  # flag to determine whether it's time for the sender to send EOT

timer = Timer()
sndpkt = {}  # dictionary of packet that has been sent, the keys are limited in the range of 0 to 31.
udpsocket = socket(AF_INET, SOCK_DGRAM)
seqlog = open("seqnum.log", "w")
DEBUG = False


def log(s):
    if DEBUG:
        print(s)


def udt_send(packet, emulatorIp, emulatorPort):
    udpsocket.sendto(packet.get_udp_data(), (emulatorIp, emulatorPort))


def rdt_send(data, emulatorIp, emulatorPort):
    # create a packet of the data, append the packet into the sndpkt list
    # each packet is associated with a sequence number
    # send the packet through udt
    # restart timer if this packet is the oldest unacknowledged packet
    sndpkt[nextseqnum] = packet.create_packet(nextseqnum, data)
    udt_send(sndpkt[nextseqnum], emulatorIp, emulatorPort)
    log("send data packet" + str(nextseqnum))
    if base == nextseqnum:
        log("base == nextseqnum, restart timer")
        timer.start()


def rdt_rcv(senderPort):
    # This is the function to run in the thread that listens to a udp socket and checks received ack packets
    log("rdt_rcv starts. ")
    global base, num_sent_packets, send_eot_flag, num_ack_packets, nextseqnum
    udpsocket_rcv = socket(AF_INET, SOCK_DGRAM)
    udpsocket_rcv.bind(('', senderPort))
    acklog = open("ack.log", "w")

    while True:
        # if the number of received ack packets equals to the number of sent data packets, set the send_eot_flag to 1.
        if num_ack_packets == num_sent_packets:
            send_eot_flag = 1

        rcvdata, emulator_adress = udpsocket_rcv.recvfrom(1024)
        rcv_packet = packet.parse_udp_data(rcvdata)
        rcv_seq_num = rcv_packet.seq_num

        if rcv_packet.type == 0:
            # type = 0 means it's a data packet.
            # the if and elif conditions ensures the received sequence number corresponds to one of the sent but not yet
            # acked packet. The distance between the received sequence number and the base is the number of packets that
            # are acked this time, so then add the distance to num_ack_packets.
            if (base < nextseqnum and base <= rcv_seq_num < nextseqnum) or (base > nextseqnum and rcv_seq_num >= base):
                num_ack_packets = num_ack_packets + (rcv_seq_num - base + 1)
                base = (rcv_seq_num + 1) % 32

            elif base > nextseqnum and rcv_seq_num < nextseqnum:
                num_ack_packets = num_ack_packets + (rcv_seq_num + 32 - base + 1)
                base = (rcv_seq_num + 1) % 32

            acklog.write(str(rcv_seq_num) + '\n')

            if base == nextseqnum:
                # no more sent but not yet acked packets, so stop timer
                log("receive acks" + str(rcv_seq_num) + ", no more sent packets, stop timer.\n")
                timer.stop()
            else:
                # restart the timer for the next sent but not yet acked packet
                log("receive acks" + str(rcv_seq_num) + ", restart timer.\n")
                timer.start()

        elif rcv_packet.type == 2:
            # type = 2 means it's an EOT packet. If receiving EOT, then exit.
            break

    acklog.close()


def timeout_event(emulatorIp, emulatorPort):
    # if timeout, restart timer and send all unacked packets
    log("timeout, restart timer. ")
    timer.start()
    i = base
    while (base < nextseqnum and base <= i < nextseqnum) or (nextseqnum < base <= i < nextseqnum + 32):
        k = i % 32
        udt_send(sndpkt[k], emulatorIp, emulatorPort)
        seqlog.write(str(k) + "\n")
        log("send data packet" + str(k) + '\n')
        i += 1
    log("resend unacked packets. ")


def main():
    emulatorIp = sys.argv[1]
    emulatorPort = int(sys.argv[2])
    senderPort = int(sys.argv[3])
    file = sys.argv[4]
    sent_packets_count = 0

    # start the thread for checking received acknowledgments
    t1 = threading.Thread(target=rdt_rcv, args=(senderPort,))
    t1.start()

    transmission_start_time = time.monotonic()

    # read data from file into pieces and send them via udt
    with open(file, "r") as f:
        while True:
            piece = f.read(MAX_DATA_SIZE)  # read data into MAX_DATA_SIZE bytes pieces
            if piece == "":  # EOF
                break
            # keep checking window and timeout until the window is not full (then send the piece of data)
            # or timeout (then resend all unacked packets).
            global nextseqnum, base
            while True:
                if timer.time_elapsed() < timeout:
                    if (base <= nextseqnum < base + n) or (nextseqnum < base and nextseqnum + 32 < base + n):
                        # send data only when the window is not full
                        rdt_send(piece, emulatorIp, emulatorPort)
                        sent_packets_count += 1
                        seqlog.write(str(nextseqnum) + "\n")
                        nextseqnum += 1
                        nextseqnum = nextseqnum % 32
                        break
                else:
                    # timeout
                    timeout_event(emulatorIp, emulatorPort)

    global num_sent_packets, num_ack_packets
    num_sent_packets = sent_packets_count

    # all packets have been sent, wait for send_eot_flag to send EOT. In the meanwhile, keep checking timeout.
    while True:
        if send_eot_flag == 1:
            udt_send(packet.create_eot(nextseqnum), emulatorIp, emulatorPort)
            log("sender sends eot")
            break
        elif timer.time_elapsed() >= timeout:
            timeout_event(emulatorIp, emulatorPort)

    t1.join()
    log("rdt_rcv stops")

    seqlog.close()

    # record transmission time
    transmission_end_time = time.monotonic()
    transmission_time = transmission_end_time - transmission_start_time
    with open("time.log", "a") as timelog:
        timelog.write(str(transmission_time) + '\n')
    log("transmission time is " + str(transmission_time) + "s")

    exit(0)


if __name__ == '__main__':
    main()
