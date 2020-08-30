"""
vrouter.py;
This is to fulfill the requirement of A3 of CS656 of University of Waterloo
A program of a virtual router:
- receive/send topology information from/to other routers
- keep a topology database
- keep a graph representation of the network topology
- run dijkstra algorithm to generate routing table
- keep a routing table
"""

from socket import *
from nfe import *
import sys

DEBUG = False


def log(s):
    if DEBUG:
        print(s)


class TopologyEntry:
    """Topology entry to be saved in TopologyDB. """
    def __init__(self, router1, link, router2):
        self.router1 = router1
        self.router2 = router2
        self.link = link

    def isComplete(self):
        """check whether an entry contains complete information about router 1, router 2, and the link. """
        if (self.router1 is not None) and (self.router2 is not None) and (self.link is not None):
            return True
        return False


class TopologyDB:
    """Topology databse, consisting topology entries. """
    def __init__(self):
        self.topology_db = []
        self.complete_entry_list = []

    def add_entry(self, topology_entry):
        self.topology_db.append(topology_entry)

    def add_to_complete_list(self, entry):
        """ reverse_entry: with routers in opposite directions compared to the input entry """
        reverse_entry = TopologyEntry(entry.router2, entry.link, entry.router1)
        self.complete_entry_list.append(entry)
        self.complete_entry_list.append(reverse_entry)

    def update(self, lsa, vrouter_id, graph, routing_table):
        """
        Every time a new LSA is received. (The new LSA wasn't received before.)
        - update topology database
        - if the LSA matches with a current entry and complete it
            - output topology to topology_i.out file
            - add an edge to graph
            - run shortest path algorithm and output routing table
        """
        link_exist = False
        for entry in self.topology_db:
            if entry.link.id == lsa.router_link_id:
                link_exist = True

                # complete the information of an entry
                if entry.router1 is not None and entry.router1 != lsa.router_id:
                    entry.router2 = lsa.router_id
                elif entry.router2 is not None and entry.router2 != lsa.router_id:
                    entry.router1 = lsa.router_id

                # output complete entries from database.
                self.add_to_complete_list(entry)
                self.output_to_file(vrouter_id)

                # each complete entry corresponds to an edge in the graph. Add the edge to graph.
                graph.add_edge(entry.router1, entry.router2, entry.link.cost)

                # run dijkstra algorithm, generate routing table
                routing_table.gen_routing_table(graph, vrouter_id)

        if not link_exist:
            link = Link(lsa.router_link_id, lsa.router_link_cost)
            entry = TopologyEntry(lsa.router_id, link, None)
            self.topology_db.append(entry)

    def output_to_file(self, vrouter_id):
        """ Write complete topology entries to file """
        if len(self.complete_entry_list) == 0:
            return
        filename = "topology_{0}.out".format(vrouter_id)
        fd = open(filename, 'a')
        fd.write('TOPOLOGY\n')
        for entry in self.complete_entry_list:
            fd.write('router:{0},router:{1},linkid:{2},cost:{3}\n'.format
                     (entry.router1, entry.router2, entry.link.id, entry.link.cost))
        fd.close()


class LSA:
    """ LSA messages """
    def __init__(self, buffer=None, sender_id=None, sender_link_id=None, router_id=None,
                 router_link_id=None, router_link_cost=None):
        self.buffer = buffer
        self.msg_type = 3
        self.sender_id = sender_id
        self.sender_link_id = sender_link_id
        self.router_id = router_id
        self.router_link_id = router_link_id
        self.router_link_cost = router_link_cost

    def pack(self):
        """ pack a msg into a buffer (bytearray)"""
        self.buffer = None
        self.buffer = struct.pack('!i', self.msg_type)
        self.buffer += struct.pack('!i', self.sender_id)
        self.buffer += struct.pack('!i', self.sender_link_id)
        self.buffer += struct.pack('!i', self.router_id)
        self.buffer += struct.pack('!i', self.router_link_id)
        self.buffer += struct.pack('!i', self.router_link_cost)

    def unpack(self):
        """ unpack a buffer into a msg """
        data = struct.unpack('!iiiiii', self.buffer)
        self.msg_type = data[0]
        self.sender_id = data[1]
        self.sender_link_id = data[2]
        self.router_id = data[3]
        self.router_link_id = data[4]
        self.router_link_cost = data[5]


class SavedLSAPayload:
    """
    Stores the payload (router_id, router_link_id) of each received LSA.
    Used to check whether a new incoming LSA was received or not.
    """
    def __init__(self):
        self.payloads = []

    def isExist(self, lsa):
        if (lsa.router_id, lsa.router_link_id) in self.payloads:
            return True
        return False

    def add_payload(self, lsa):
        if not self.isExist(lsa):
            self.payloads.append((lsa.router_id, lsa.router_link_id))
        else:
            print("error: the payload cannot be added as it is exist. ")


class Vertex:
    """ Vertex in a graph """
    def __init__(self, id):
        """
        id: vertex id
        neighbours: adjacency dictionary. key is a neighbour vertex, value is the cost of the edge between them
        dist: distance between the vertex to the source vertex.
        visited: if the vertex has been visited in dijkstra algorithm
        prev: the predecessor of the vertex in a shortest path
        """
        self.id = id
        self.neighbours = {}
        self.dist = sys.maxsize
        self.visited = False
        self.prev = None

    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def add_neighbour(self, neighbour, cost):
        self.neighbours[neighbour] = cost

    def get_cost(self, neighbour):
        return self.neighbours[neighbour]


class Graph:
    """ graph """
    def __init__(self):
        self.vertex_dict = {}
        self.num_vertices = 0

    def add_vertex(self, vertex_id):
        self.num_vertices += 1
        new_vertex = Vertex(vertex_id)
        self.vertex_dict[vertex_id] = new_vertex
        return new_vertex

    def get_vertex(self, vertex_id):
        if vertex_id in self.vertex_dict:
            return self.vertex_dict[vertex_id]
        return None

    def add_edge(self, v1_id, v2_id, cost):
        self.edge_exist = True
        if v1_id not in self.vertex_dict:
            self.add_vertex(v1_id)
        if v2_id not in self.vertex_dict:
            self.add_vertex(v2_id)

        self.vertex_dict[v1_id].add_neighbour(self.vertex_dict[v2_id], cost)
        self.vertex_dict[v2_id].add_neighbour(self.vertex_dict[v1_id], cost)

    def dijkstra_init(self):
        for v in self.vertex_dict.values():
            v.dist = sys.maxsize
            v.prev = None
            v.visited = False

    def dijkstra(self, source_id):
        """ dijkstra algorithm to calculate the shortest path from a source vertex """
        self.dijkstra_init()

        source = self.get_vertex(source_id)
        source.dist = 0;
        unvisited_list = self.vertex_dict.values()  # list of all vertices in the graph

        while len(unvisited_list) > 0:
            # sort the unvisited list to find the vertex with the shortest distance
            unvisited_list = sorted(unvisited_list, key=lambda x: x.dist)
            u = unvisited_list[0]  # u is the vertex with min distance
            unvisited_list.remove(unvisited_list[0])  # remove u from the unvisited list
            u.visited = True

            # relaxation
            for v in u.neighbours:
                if not v.visited:
                    alt_dist = u.dist + u.get_cost(v)
                    if alt_dist < v.dist:
                        v.dist = alt_dist
                        v.prev = u


class RoutingEntry:
    """ A routing entry in the routing table """
    def __init__(self, destination, next_hop, cost):
        self.dest = destination
        self.next_hop = next_hop
        self.cost = cost

    def to_string(self):
        string = '{0}:{1},{2}\n'.format(self.dest.id, self.next_hop.id, self.cost)
        return string

    def __eq__(self, other):
        if isinstance(other, RoutingEntry):
            # return (self.dest.id, self.next_hop.id, self.cost) == (other.dest.id, other.next_hop.id, other.cost)
            return self.dest.id == other.dest.id and self.next_hop.id == other.next_hop.id and self.cost == other.cost
        return False

    def __hash__(self):
        return hash((self.dest.id, self.next_hop.id, self.cost))


class RoutingTable:
    """ routing table """
    def __init__(self):
        self.routing_table = []

    def need_to_update_table(self, temp_table):
        """
        temp table is the result after the graph is updated and the dijkstra algorithm runs.
        checks whether the update of the graph has led to changes in the routing table
        if table is changed, output routing table to file; otherwise, do not output.
        """
        for entry in temp_table:
            if entry not in self.routing_table:
                return True
        return False

    def gen_routing_table(self, graph, source_id):
        """
        - run dijkstra algorithm to generate a new routing table
        - check if need_to_update_table
        """
        # if source vertex wasn't added to the graph, it means the source vertex doesn't have neigbours yet.
        # no routing table should be generated
        if source_id not in graph.vertex_dict:
            return

        temp_routing_table = []
        graph.dijkstra(source_id)
        for v in graph.vertex_dict.values():
            if v.id != source_id and v.dist < sys.maxsize:
                routing_entry = RoutingEntry(None, None, None)
                routing_entry.dest = v
                routing_entry.cost = v.dist
                while v.prev.id != source_id:
                    v = v.prev
                routing_entry.next_hop = v
                temp_routing_table.append(routing_entry)

        if self.need_to_update_table(temp_routing_table):
            self.routing_table.clear()
            for entry in temp_routing_table:
                self.routing_table.append(entry)
            self.output_table(source_id)

    def output_table(self, source_id):
        """ output the routing table into file routingtable_i.out"""
        fd = open('routingtable_{0}.out'.format(source_id), 'a')
        fd.write('ROUTING\n')
        self.routing_table = sorted(self.routing_table, key=lambda x : x.dest.id)
        for entry in self.routing_table:
            fd.write(entry.to_string())
        fd.close()


def vrouter_stdout(mode, lsa):
    """print to stdout the information about messages sending, received and dropping """
    sid = lsa.sender_id
    slid = lsa.sender_link_id
    rid = lsa.router_id
    rlid = lsa.router_link_id
    lc = lsa.router_link_cost

    if mode == 'E' or mode == 'F':
        sys.stdout.write(
            "Sending({0}):SID({1}),SLID({2}),RID({3}),RLID({4}),LC({5})\n".format(mode, sid, slid, rid, rlid, lc))
    elif mode == 'R':
        sys.stdout.write("Received:SID({0}),SLID({1}),RID({2}),RLID({3}),LC({4})\n".format(sid, slid, rid, rlid, lc))
    elif mode == 'D':
        sys.stdout.write("Dropping:SID({0}),SLID({1}),RID({2}),RLID({3}),LC({4})\n".format(sid, slid, rid, rlid, lc))


def main():
    nfe_ip = sys.argv[1]
    nfe_port = int(sys.argv[2])
    vrouter_id = int(sys.argv[3])
    nfe_address = (nfe_ip, nfe_port)

    topology_db = TopologyDB()  # topology database
    graph = Graph()  # a graph
    routing_table = RoutingTable()  # routing table
    sock = socket.socket(AF_INET, SOCK_DGRAM)

    # stage 1: send init message to nfe
    init_msg = struct.pack('!i', 1)  # message type 0x01
    init_msg += struct.pack('!i', vrouter_id)  # router id
    sock.sendto(init_msg, nfe_address)

    # stage 2: listen and wait for init_reply message, create topology entries and store them in the database
    link_list = []
    while True:
        reply_buffer, address = sock.recvfrom(4096)
        reply_msg_type = struct.unpack('!i', reply_buffer[:4])[0]
        if reply_msg_type != 4:
            sys.stderr.write("error: init reply message type error")
            continue
        num_links = struct.unpack('!i', reply_buffer[4:8])[0]
        offset = 8
        while num_links > 0:
            link_id = struct.unpack('!i', reply_buffer[offset: offset + 4])[0]
            offset += 4
            link_cost = struct.unpack('!i', reply_buffer[offset: offset + 4])[0]
            offset += 4
            topology_db.add_entry(TopologyEntry(vrouter_id, Link(link_id, link_cost), None))
            link_list.append(Link(link_id, link_cost))
            num_links -= 1
        break

    # stage 3: forwarding phase
    # stage 3.1: initially emitting LSA
    for link in link_list:
        for entry in topology_db.topology_db:
            lsa = LSA(sender_id=vrouter_id, sender_link_id=link.id, router_id=entry.router1,
                      router_link_id=entry.link.id, router_link_cost=entry.link.cost)
            lsa.pack()
            sock.sendto(lsa.buffer, nfe_address)
            vrouter_stdout('E', lsa)

    # stage 3.2: wait to receive LSA, then forward it to neighbours or drop/ignore it
    saved_payloads = SavedLSAPayload()
    while True:
        lsa_buffer, address = sock.recvfrom(4096)
        lsa = LSA(buffer=lsa_buffer)
        lsa.unpack()
        vrouter_stdout('R', lsa)

        # if the LSA was received, ignore the msg
        if saved_payloads.isExist(lsa):
            vrouter_stdout('D', lsa)
            continue

        # if the LSA wasn't received, record its payload, update topology database, update graph and write to output
        # file
        saved_payloads.add_payload(lsa)
        topology_db.update(lsa, vrouter_id, graph, routing_table)

        # modify sender_id and sender_link_id, and forward the message through each link
        lsa.sender_id = vrouter_id
        income_link_id = lsa.sender_link_id
        for link in link_list:
            if link.id != income_link_id:
                lsa.sender_link_id = link.id
                lsa.pack()
                sock.sendto(lsa.buffer, nfe_address)
                vrouter_stdout('F', lsa)


if __name__ == '__main__':
    main()
