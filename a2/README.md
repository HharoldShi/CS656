# Command to run a receiver:

./receiver.sh 
<hostname for the network emulator>,
<UDP port number used by the emulator to receive ACKs from the receiver>,
<UDP port number used by the receiver to receive data from the emulator>,
<name of the file into which the received data is written>

for example: ./receiver.sh ubuntu1804-002.student.cs.uwaterloo.ca 10023 10024 'destination_file.txt'


# Command to run a sender:

./sender.sh 
<host address of the network emulator>,
<UDP port number used by the emulator to receive data from the sender>, 
<UDP port number used by the sender to receive ACKs from the emulator>, 
<name of the file to be transferred>

for example: ./sender.sh ubuntu1804-002.student.cs.uwaterloo.ca 10021 10022 'tiny.txt'


# Command to run the emulator:

./nEmulator-linux386 
<emulator's receiving UDP port number in the forward (sender) direction>, 
<receiver’s network address>,
<receiver’s receiving UDP port number>,
<emulator's receiving UDP port number in the backward (receiver) direction>,
<sender’s network address>,
<sender’s receiving UDP port number>,
<maximum delay of the link in units of millisecond>, <packet discard probability>,
<verbose-mode>

For example: ./nEmulator-linux386 10021 ubuntu1804-004.student.cs.uwaterloo.ca 10024 10023 ubuntu1804-008.student.cs.uwaterloo.ca 10022 1 0.2 0


The programs are tested on ubuntu1804-002.student.cs.uwaterloo.ca, ubuntu1804-004.student.cs.uwaterloo.ca,
and ubuntu1804-008.student.cs.uwaterloo.ca.

Since programs are written in Python3, no make or compilers are used.

