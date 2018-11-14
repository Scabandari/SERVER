import ast
import threading
from utils import (dict_to_bytes,
                   name_registered,
                   update_txt_file,
                   recover_state,
                    top_bidder,
                   name_matches_ip,
                   has_open_items,
                   under_three_opens,
                   client_connected,
                   is_ip,
                   getItemDescriptions)
# referenced here: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


class ClientConnection(threading.Thread):
    def __init__(self, ip, port, connection, state, state_lock, txt_file):
        self.ip = ip
        self.port = port
        self.connection = connection
        self.state = state
        self.txt_file = txt_file
        self.state_lock = state_lock
        #self.OFFER = 'OFFER'
        threading.Thread.__init__(self)
        print("Starting tcp socket connection with client at " + str(ip) + " port " + str(port))

    def run(self):
        """This class functions as its own thread. The run function is what the thread does"""
        print("ClientConnection run method started")
        while True:
            # data = connection.recv(1024).decode('ascii')
            data = self.connection.recv(1024).decode('utf-8')
            if not data:
                #print("Data is not correct")
                break
            msg_received = ast.literal_eval(data)
            print("Message received from client over tcp: {}".format(data)) # For testing purposes
            return_msg = self.handle_response(msg_received)
            return_msg = dict_to_bytes(return_msg)
            self.send_msg(return_msg)

    def handle_response(self, msg_received):
        #Message will always be a bid. What this function will do is check whether to send the Winner and
        #the highest bid messages, in addition to the general bid confirmed message
        print('hello')
        msg = 'hello'
        return msg

    def send_msg(self, msg):
        """msg: a dict to be sent to the client"""
        msg = str(msg)
        self.connection.send(msg.encode('utf-8'))




