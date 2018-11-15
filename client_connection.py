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
                   getItemDescriptions,
                   getItem,
                   getHighestBid)
# referenced here: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


class ClientConnection(threading.Thread):
    BID = 'BID' #when bid is good, meaning its the highest bid
    BID_LOW = 'BID_LOW'

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
            #return_msg = self.handle_response(msg_received)
            #return_msg = dict_to_bytes(return_msg)
            return_msg = "Nothing yet" #bidding process not complete yet, will crash if activated.
            self.send_msg(return_msg)

    def handle_response(self, msg_received):
        #Message will always be a bid. What this function will do is check whether to send the Winner and
        #the highest bid messages, in addition to the general bid confirmed message
        print("msg_received: {}".format(str(msg_received)))  #FOR TESTING PURPOSES
        type_ = msg_received['type']
        #Only one type but this format makes it easy to scale if we want
        #to add more functionality
        if (type_ == ClientConnection.BID):
            response = self.ack_bid(msg_received)
        else:
            print("ERROR: TCP msg received with unknown type")  # todo change this
            error_msg = "Cannot handle msg of type: {}".format(msg_received['type'])
            response = {'ERROR': 'Unknown type'}  # todo fix this, need a better response
            print(error_msg)
        return response

    def ack_bid(self, msg_received):
        amount = int(msg_received['amount'])
        itemForBid = getItem(self.port, self.state)
        currentMaxBid = getHighestBid(itemForBid)
        #converting into int to use in comparator
        if (amount <= currentMaxBid):
            response = self.respond_bid(msg_received, False)
        else:
            response = self.respond_bid(msg_received,True)
        return response

    def respond_bid(self, msg_received, success):
        #Responds to the bid 
        if success is True:
            msg = {
                'type:':'BID',
                'request:':msg_received['request'],
                'highest bid':msg_received['highest bid'],
                'item #':msg_received['item #']
            }
        else:
            msg = {
                'type:':'BID_LOW',
                'request:':msg_received['request'],
                'minimum bid:':msg_received['minimum bid'],
                'reason:': 'your bid is too low, MO MONEY!'
            }
        return msg

    def send_msg(self, msg):
        """msg: a dict to be sent to the client"""
        msg = str(msg)
        self.connection.send(msg.encode('utf-8'))




