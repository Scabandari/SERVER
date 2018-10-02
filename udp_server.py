import threading
import socket
import ast
from utils import dict_to_bytes, check_name


class UDPServer(threading.Thread):
    REGISTER = 'REGISTER'
    REGISTERED = 'REGISTERED'
    UNREGISTERED = 'UNREGISTERED'
    UNKNOWN = 'UNKNOWN'

    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state, state_lock):
        self.host = host
        self.port = port
        self.state = state
        self.state_lock = state_lock  # locks access to state, update .txt file while lock held
        self.continue_thread = True
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((host, port))
        threading.Thread.__init__(self)

    def run(self):
        print("UDP connection started on server side.")
        while self.continue_thread:
            # todo we should have a pool of threads here for client connections?
            data, addr = self.udp_socket.recvfrom(1024)
            data = data.decode('ascii')  # data.decode('utf-8')
            msg_received = ast.literal_eval(data)  # unpacked as a dict object
            error_msg = self.handle_response(msg_received, addr)
            request_number = msg_received['request']
            if error_msg:
                self.send_back_error(error_msg, type, request_number, addr)
        self.udp_socket.close()
        print("UDPServer run function complete. UDP socket connection closed")

    def ack_register_attempt(self, msg_received, return_address):
        """this function should return a msg to the sender that the registration is successful or not
            and if so update internal state to reflect that as well as update the .txt file"""
        # todo some type checking for port numbers and ip addresses would be good
        name = msg_received['name']
        ip = msg_received['ip']
        response = msg_received
        request_number = msg_received['request']
        print("Received request#: {} from: {} @ address: {}".format(request_number, name, ip))

        if check_name(name, self.state):
            self.state['names'].append((name, ip))
            print("{} registration acknowledged".format(name))
            response['type'] = UDPServer.REGISTERED
        else:
            print("{} registration not acknowledged. Duplicate names".format(name))
            response = {'request': request_number, 'type': UDPServer.UNREGISTERED, 'reason': 'Duplicate names'}
        response = dict_to_bytes(response)
        self.udp_socket.sendto(response, return_address)

    def handle_response(self, msg_received, return_address):
        """This function accepts the incoming dict and checks the type so it
            can call the corresponding ack function. If this function can't identify
            the proper type it will return a string of the error msg"""
        if msg_received['type'] == UDPServer.REGISTER:
            self.ack_register_attempt(msg_received, return_address)
        else:
            print("type != Register threfore do nothing")  # todo change this
            error_msg = "Cannot handle msg of type: {}".format(msg_received['type'])
            return error_msg

    def send_back_error(self, error_msg, type_, request_number, return_address):
        """This function should send back an error regardless of type so
            will be expanded to become and if elsif elsif ...."""
        if type_ == UDPServer.REGISTER:
            response_type = UDPServer.UNREGISTERED
        else:
            response_type = UDPServer.UNKNOWN
            error_msg = "Unable to determine msg type"
        response = {'type': response_type, 'request': request_number, 'reason': error_msg}
        response = dict_to_bytes(response)
        self.udp_socket.sendto(response, return_address)

