import threading
import socket
import ast
import time
from tcp_server import TCPServer
from utils import (dict_to_bytes,
                   name_registered,
                   update_txt_file,
                   recover_state,
                    top_bidder,
                   name_matches_ip,
                   has_open_items,
                   under_three_opens,
                   client_connected,
                   is_ip)


class UDPServer(threading.Thread):
    REGISTER = 'REGISTER'
    REGISTERED = 'REGISTERED'
    UNREGISTERED = 'UNREGISTERED'
    DE_REGISTER = 'DE-REGISTER'
    DEREG_CONF =  'DEREG-CONF'
    DEREG_DENIED = 'DEREG-DENIED'
    UNKNOWN = 'UNKNOWN'
    OFFER = 'OFFER'
    NEW_ITEM = 'NEW-ITEM'

    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state, state_lock, txt_file):
        self.next_item = 1
        self.host = host
        self.port = port
        self.item_port = 5050  # the next port to assign for an item on offer, clients connect here to a TCPServer
                               # bound to this port
        self.state = state
        self.txt_file = txt_file
        self.connected_clients = []  # [(ip, port), (ip, port)...]
        self.item_servers = []
        self.state_lock = state_lock  # locks access to state, update .txt file while lock held
        self.continue_thread = True
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((host, port))
        threading.Thread.__init__(self)

    def run(self):
        print("UDP connection started on server side.")
        while self.continue_thread:
            data, return_address = self.udp_socket.recvfrom(1024)
            if not client_connected(return_address, self.connected_clients):
                self.connected_clients.append(return_address)
            data = data.decode('ascii')  # data.decode('utf-8')
            msg_received = ast.literal_eval(data)  # unpacked as a dict object
            return_msg = self.handle_response(msg_received)
            return_msg = dict_to_bytes(return_msg)
            self.udp_socket.sendto(return_msg, return_address)
        self.udp_socket.close()
        print("UDPServer run function complete. UDP socket connection closed")

    def ack_de_register(self, msg_received):
        """
        If the client from which msg_received is sent is registered, has no items open for bids,
        name and ip must match what is stored in their registration in state, they're not the top bidder
        on any open items then deregister them and return a success msg. Otherwise return a msg indicating why
        they cannot de-register
        :param msg_received: msg received from client
        :return: msg response for client
        """
        can_de_reg = True
        name = msg_received['name']
        ip = msg_received['ip']
        request_number = msg_received['request']
        if not name_registered(name, self.state):
            can_de_reg = False
            reason = "That name not registered"
        elif not is_ip(ip):
            can_de_reg = False
            reason = "That ip is not a valid ip address: {}".format(ip)
        elif not name_matches_ip(name, ip, self.state):
            can_de_reg = False
            reason = "That ip does not match the ip associated with client: {}".format(name)
        elif top_bidder(name, self.state):
            can_de_reg = False
            reason = "Cannot de-register while holding the top bid on an open item"
        elif has_open_items(name, self.state):
            can_de_reg = False
            reason = "Cannot de-register while having items listed as open for bidding"
        if can_de_reg:
            self.de_reg_success(name)  # remove from state & update txt file
            response = {
                'type': UDPServer.DEREG_CONF,
                'request': request_number
            }
        else:
            response = {
                'type': UDPServer.DEREG_DENIED,
                'request': request_number,
                'reason': reason
            }
        return response

    def ack_register(self, msg_received):
        """this function should return a msg that the registration is successful or not
            and if so update internal state to reflect that as well as update the .txt file"""
        # todo some type checking for port numbers and ip addresses would be good
        name = msg_received['name']
        response = msg_received
        request_number = msg_received['request']
        ip = msg_received['ip']
        port = msg_received['port']
        print("Received request#: {} from: {} @ address: {}".format(request_number, name, ip))

        if name_registered(name, self.state):  # todo name_registered should verify ip address as well as port#??
            print("{} registration not acknowledged. Duplicate names".format(name))
            response = {
                'request': request_number,
                'type': UDPServer.UNREGISTERED,
                'reason': 'Duplicate names'
            }
        elif not is_ip(ip):
            print("{} registration not acknowledged. Invalid ip address: {}".format(name, ip))
            response = {
                'request': request_number,
                'type': UDPServer.UNREGISTERED,
                'reason': 'Invalid ip address'
            }
        else:  # we can de-register client
            client = {'name': name,
                      'ip': ip,
                      'port': port}
            with self.state_lock:
                self.state['clients'].append(client)
                update_txt_file(self.state, self.txt_file)
            # todo just for testing. HOW TO RECOVER STATE
            # self.state = {}
            # self.state = recover_state(self.txt_file)
            print("{} registration acknowledged".format(name))
            response['type'] = UDPServer.REGISTERED
        return response

    def ack_offer(self, msg_received):
        """This functions receives the msg where a client has attempted to make and OFFER for
            an item for bid. It needs to determine if the offer is valid, possibly update
            state/txt_file and returns a response, either success or failure"""
        # todo test all possible paths
        name = msg_received['name']
        if not name_registered(name, self.state):
            # todo this should check all conditions that lead to failure and last option should be success
            reason = "Name: {} is not registered".format(name)
            response = self.respond_offer(msg_received, False, reason)
        elif not under_three_opens(name, self.state):
            reason = "Cannot have more than 3 items up for bid"
            response = self.respond_offer(msg_received, False, reason)
        else:
            print("Bid starting at time.time(): {}".format(time.time()))
            # todo broadcast new item msg to all registered clients on success
            item = self.offer_success(msg_received)
            response = self.respond_offer(msg_received, True)
            all_clients_msg = {
                'type': UDPServer.NEW_ITEM,
                'description': response['description'],
                'minimum bid': response['minimum bid'],
                'item #': response['item #'],
                'port #': item['port #']
            }
            self.send_all_clients(all_clients_msg)
            # WE CREATE A TCP SERVER FOR EVERY ITEM ON OFFER!!
            server_for_item = TCPServer(self.host, item['port #'], self.state, self.state_lock, self.txt_file)
            server_for_item.start()
            self.item_servers.append(server_for_item)
        return response

    def send_all_clients(self, msg):
        """
        This functions sends msg to all clients in self.connected_clients
        :param msg:
        :return: None
        """
        # todo We're sending the NEW-ITEM msg to all clients but we're only supposed to send it
        # todo registered clients?
        for client_address in self.connected_clients:
            send_msg = dict_to_bytes(msg)
            self.udp_socket.sendto(send_msg, client_address)

    def offer_success(self, msg):
        """Updates state and the text file and returns a msg to be sent back to
            client"""
        # todo get a random port and assign it below but first make sure not being used by other items in open list
        item = {
            'description': msg['description'],
            'minimum bid': msg['minimum bid'],
            'seller': msg['name'],
            'highest bid': (msg['minimum bid'], None),
            'open status': True,
            'starting time': time.time(),
            'port #': self.item_port
        }
        self.item_port += 1
        with self.state_lock:
            self.state['items open'].append(item)
            update_txt_file(self.state, self.txt_file)
        return item

    def de_reg_success(self, name):
        """This function should remove the client from the clients list which de-registers them.
            It also should update the txt file"""
        clients = self.state['clients']
        index_to_pop = None
        with self.state_lock:
            for index, client in enumerate(clients):
                if client['name'] == name:
                    index_to_pop = index
                    continue
            if index_to_pop is not None:
                clients.pop(index)
            update_txt_file(self.state, self.txt_file)
            print("killing time")

    def respond_offer(self, msg, success, reason=None):
        """This function is called to respond to the clients OFFER type msg"""
        if success is True:
            msg = {
                'type': 'OFFER-CONF',
                'request': msg['request'],
                'description': msg['description'],
                'minimum bid': msg['minimum bid'],
                'item #': self.next_item
            }
            self.next_item += 1
        else:
            msg = {
                'type': 'OFFER-DENIED',
                'request': msg['request'],
                'reason': reason
            }
        return msg

    def handle_response(self, msg_received):
        """This function accepts the incoming dict and checks the type so it
            can call the corresponding ack function. It should return both a success msg
            and an error msg, one of which should = None"""
        print("type(msg_received: {}".format(type(msg_received)))  # todo delete
        print("msg_received: {}".format(str(msg_received)))  # todo delete
        type_ = msg_received['type']
        if type_ == UDPServer.REGISTER:
            response = self.ack_register(msg_received)
        elif type_ == UDPServer.DE_REGISTER:
            response = self.ack_de_register(msg_received)
        elif type_ == UDPServer.OFFER:
            response = self.ack_offer(msg_received)
        else:
            print("ERROR: UDP msg received with unknown type")  # todo change this
            error_msg = "Cannot handle msg of type: {}".format(msg_received['type'])
            response = {'ERROR': 'Unknown type'}  # todo fix this, need a better response
            print(error_msg)
        return response


