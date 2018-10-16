import socket
import time
import ast
import threading
from utils import bytes_to_dict, check_name, update_txt_file
# referenced here: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


class ClientConnection(threading.Thread):
    def __init__(self, ip, port, connection, state, state_lock, txt_file):
        self.next_item = 1
        self.ip = ip
        self.port = port
        self.connection = connection
        self.state = state
        self.txt_file = txt_file
        self.state_lock = state_lock
        self.OFFER = 'OFFER'
        threading.Thread.__init__(self)
        print("Starting tcp socket connection with client at " + str(ip) + " port " + str(port))

    def run(self):
        print("ClientConnection run method started")
        while True:
            # data = connection.recv(1024).decode('ascii')
            data = self.connection.recv(1024).decode('utf-8')
            if not data:
                print("Data is not correct")
                break
            # todo below we need to examine the msg and decide what to do
            #data = ast.literal_eval(data)
            data = ast.literal_eval(data)
            self.receive_client_msg(data)
            #self.connection.send("Successful response over tcp".encode('utf-8'))

    def receive_client_msg(self, msg):
        #msg = bytes_to_dict(msg)
        #msg = ast.literal_eval(msg)
        if msg['type'] == self.OFFER:
            print("Received msg from client over tcp of type: {}".format(msg['type']))
            if not check_name(msg['name'], self.state):  # todo check also if client has 3 items already up for bid
                # todo handle_offer_success()
                # todo just for testing
                print("Bid starting at time.time(): {}".format(time.time()))
            # todo broadcast new state to all registered clients on success in addition to current response?
                self.handle_offer_success(msg)
            else:
                self.respond_offer(msg, False)
        else:
            print("Wrong type")

    def handle_offer_success(self, msg):
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
        self.respond_offer(msg, True)

    def respond_offer(self, msg, success):
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
        response_val = str(msg).encode('utf-8')
        print("response_val type: {}".format(type(response_val)))
        self.connection.send(response_val)