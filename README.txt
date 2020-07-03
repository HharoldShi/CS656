Command to run a server:
./server.sh <req_code>
for example: ./server.sh 10

Command to run a client:
./client.sh <server_address> <n_port> <req_code> ‘<message>’
for example: ./client.sh ubuntu1804-002.student.cs.uwaterloo.ca 53000 10 'message 1'

Note: please ensure both server.sh and client.sh have the permission to be executed.
if encounter response like "permission denied" when running program using the above method,
use command "chmod 755 server.sh" to change the file permission.

The programs are tested on ubuntu1804-002.student.cs.uwaterloo.ca, ubuntu1804-004.student.cs.uwaterloo.ca,
and ubuntu1804-008.student.cs.uwaterloo.ca.

Since programs are writeen in Python3, no make or compilers are used.


nEmulator-linux386 9991 localhost 9994 9993 host3 9992 1 0.2 0
