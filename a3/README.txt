# Command to run a virtual router:

./vrouter.sh <nfe-ip> <nfe-port> <virtual-router-id>
for example: ./vrouter.sh localhost 2000 1


# Command to run the Network Forwarding Emulator (NFE):
python3 nfe.py <IP> <port> <topo_filepath>

For example: python3 nfe.py localhost 2000 grading_topo.json


The programs are tested on ubuntu1804-002.student.cs.uwaterloo.ca

Since programs are written in Python3, no make or compilers are used.

