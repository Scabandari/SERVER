import threading
import socket
import ast
import time
from utils import (dict_to_bytes,
                   name_registered,
                   update_txt_file,
                   recover_state,
                    top_bidder,
                   name_matches_ip,
                   has_open_items)

# TODO right now tcp is handling OFFER but it's supposed to be done over UDP


class UDPServer(threading.Thread):
    REGISTER = 'REGISTER'
    REGISTERED = 'REGISTERED'
    UNREGISTERED = 'UNREGISTERED'
    DE_REGISTER = 'DE-REGISTER'
    DEREG_CONF =  'DEREG-CONF'
    DEREG_DENIED = 'DEREG-DENIED'
    UNKNOWN = 'UNKNOWN'
    OFFER = 'OFFER'

    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state, state_lock, txt_file):
        self.next_item = 1
        self.host = host
        self.port = port
        self.state = state
        self.txt_file = txt_file
        self.state_lock = state_lock  # locks access to state, update .txt file while lock held
        self.continue_thread = True
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((host, port))
        threading.Thread.__init__(self)

    def run(self):
        print("UDP connection started on server side.")
        while self.continue_thread:
            # todo we should have a pool of threads here for client connections?
            data, return_address = self.udp_socket.recvfrom(1024)
            data = data.decode('ascii')  # data.decode('utf-8')
            msg_received = ast.literal_eval(data)  # unpacked as a dict object
            return_msg = self.handle_response(msg_received)
            return_msg = dict_to_bytes(return_msg)
            self.udp_socket.sendto(return_msg, return_address)
            # todo this is where i should return the msg either success or failure
            #request_number = msg_received['request']
            # if error_msg:
            #     self.send_back_error(error_msg, type, request_number, addr)
        self.udp_socket.close()
        print("UDPServer run function complete. UDP socket connection closed")

    def ack_de_register(self, msg_received):
        # todo if they are registered and not the top bid for an item or offered an item currently being bid on
        # then success else failure
        can_de_reg = True
        name = msg_received['name']
        ip = msg_received['ip']
        request_number = msg_received['request']
        if not name_registered(name, self.state):
            can_de_reg = False
            reason = "That name not registered"
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
        if not name_registered(name, self.state):  # todo name_registered should verify ip address as well as port#??
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

        else:
            print("{} registration not acknowledged. Duplicate names".format(name))
            response = {'request': request_number, 'type': UDPServer.UNREGISTERED, 'reason': 'Duplicate names'}
        return response

    def ack_offer(self, msg_received):
        """This functions receives the msg where a client has attempted to make and OFFER for
            an item for bid. It needs to determine if the offer is valid, possibly update
            state/txt_file and returns a response, either success or failure"""
        if name_registered(msg_received['name'], self.state):  # todo check also if client has 3 items already up for bid
            # todo handle_offer_success()
            # todo just for testing
            print("Bid starting at time.time(): {}".format(time.time()))
            # todo broadcast new state to all registered clients on success in addition to current response?
            self.offer_success(msg_received)
            response = self.respond_offer(msg_received, True)
        else:
            response = self.respond_offer(msg_received, False)
        return response

    def offer_success(self, msg):
        """Updates state and the text file and returns a msg to be sent back to
            client"""
        item = {
            'description': msg['description'],
            'minimum bid': msg['minimum bid'],
            'seller': msg['name'],
            'highest bid': (msg['minimum bid'], None),
            'open status': True,
            'starting time': time.time()
        }
        with self.state_lock:
            self.state['items open'].append(item)
            update_txt_file(self.state, self.txt_file)

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

    def respond_offer(self, msg, success):
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
                'reason': 'client not registered'
            }
        #response_val = str(msg).encode('utf-8')
        #print("response_val type: {}".format(type(response_val)))
        return msg  # todo make sure this is getting sent
        #self.connection.send(response_val)   tcp stuff

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
            # todo make sure we're checking if the name and ip address are correct before de-reg
            response = self.ack_de_register(msg_received)
        elif type_ == UDPServer.OFFER:
            response = self.ack_offer(msg_received)
        else:
            # todo think about what we should do here if we can't identify the correct type
            # todo of the msg being sent to use over UDP
            # todo test this by senting an UDP message of unknown type
            print("type != Register threfore do nothing")  # todo change this
            error_msg = "Cannot handle msg of type: {}".format(msg_received['type'])
            response = {'ERROR': 'Unknown type'}  # todo fix this, need a better response
            print(error_msg)
        return response

    # def send_back_error(self, error_msg, type_, request_number, return_address):
    #     """This function should send back an error regardless of type so
    #         will be expanded to become and if elsif elsif ...."""
    #     if type_ == UDPServer.REGISTER:
    #         response_type = UDPServer.UNREGISTERED
    #     else:
    #         response_type = UDPServer.UNKNOWN
    #         error_msg = "Unable to determine msg type"
    #     response = {'type': response_type, 'request': request_number, 'reason': error_msg}
    #     response = dict_to_bytes(response)
    #     self.udp_socket.sendto(response, return_address)

