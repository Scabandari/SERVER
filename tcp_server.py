import threading
from time import sleep
import socket
from utils import get_item, get_highest_bid, get_highest_bidder, get_client
from client_connection import ClientConnection, all_client_messages, the_winning_message


"""We have a TCPServer for each item on bid, self.connection_list[] is a list of bidders ie clients
    who have successfully connected over tcp to ip + port for specific item on bid. """


class TCPServer(threading.Thread):
    HIGHEST = 'HIGHEST'
    BID_OVER = 'BID_OVER'
    BID_SOLDTO = 'BID_SOLDTO'
    BID_NOTSOLD = 'BID_NOTSOLD'
    WIN = 'WIN'

    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state, state_lock, txt_file, item_number):
        self.host = host
        self.port = port
        self.state = state
        self.txt_file = txt_file
        self.send_all_clients = []
        self.all_clients_lock = threading.Lock()
        self.state_lock = state_lock  # locks access to state, update .txt file while lock held
        self.connection_list = []
        self.count_down = 20  # change to 300 for five min auction
        self.item_number = item_number
        self.messages = []  # list of msg's or dicts sent from clients over tcp
        self.continue_thread = True  # set to False if we want to terminate thread
        self.start_listening = False
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((host, port))
        self.tcp_socket.listen(5)
        threading.Thread.__init__(self)

    def run(self):
        print("TCP connection started on server side")
        send_all_clients = threading.Thread(target=self.check_all_clients)
        send_all_clients.start()
        listen_to_clients = threading.Thread(target=self.listen_to_clients)
        listen_to_clients.start()
        count_down_timer = threading.Thread(target=self.countdown_timer)
        count_down_timer.start()
        while self.continue_thread:
            # (conn, (ip, port)) = self.tcp_socket.accept()
            (conn, addr) = self.tcp_socket.accept()
            ip = str(addr[0])
            port = str(addr[1])
            print("TCP connection from ip: {} port: {}".format(ip, port))
            connection_success = {
                'set port': True,
                'message': 'TCP connection to server success',
                'ip': ip,
                'port': port
            }
            connection_success = str(connection_success)
            conn.send(connection_success.encode('utf-8'))
            newthread = ClientConnection(addr[0], addr[1], conn, self.state, self.state_lock, self.txt_file, self.port)
            newthread.start()
            self.start_listening = True
            self.connection_list.append(newthread)

    def check_all_clients(self):
        """this function should repeatedly check the self.send_all_clients queue for
            msg's to be sent out to all clients"""
        while self.continue_thread:
            all_clients_msg = None
            with self.all_clients_lock:
                if len(self.send_all_clients) > 0:
                    all_clients_msg = self.send_all_clients.pop(0)
            if all_clients_msg:
                for client in self.connection_list:
                    print(client)
                    print("#")
                    print(all_clients_msg)
                    print("#")
                    client.send_msg(all_clients_msg)
            sleep(0.2)  # sleep 200 millis and make sure others can easily acquire all_clients_lock

    def listen_to_clients(self):
        """This function keeps listening for new messages from the clients connected to the item's tcp connection
        once it detects that a message has been sent (it will be the highest message, it processes it and adds it
        to send all clients"""
        while self.continue_thread:
            if all_client_messages:
                if not self.send_all_clients:
                    self.send_all_clients.append(all_client_messages.pop(0))
                else:
                    return_msg = all_client_messages.pop(0)
                    for msg in self.send_all_clients:

                        if msg['item #'] == return_msg['item #'] and \
                                msg['amount'] == return_msg['amount']:
                            pass
                        else:
                            self.send_all_clients.append(return_msg)
            else:
                pass

    def countdown_timer(self):
        print("Counter has started: 5 minutes till bid close on item #: " + str(self.item_number))
        sleep(self.count_down)
        print('5 minutes are over, bid will now close for item #: '+ str(self.item_number))
        self.handle_end_of_bid()
        highest_bid = get_highest_bid(get_item(self.port, self.state))
        msg = {
            'type': self.BID_OVER,
            'item #': self.item_number,
            'amount': highest_bid
        }
        self.send_all_clients.append(msg)

    def winning_bid(self, item):
        highest_bid = get_highest_bid(item)
        highest_bidder = get_highest_bidder(item)
        client = get_client(highest_bidder, self.state)
        msg = {
            'type': self.WIN,
            'item #': self.item_number,
            'name': client['name'],
            'ip address': client['ip'],
            'port #': client['port'],
            'amount': highest_bid
        }
        the_winning_message.append(msg)

    def handle_end_of_bid(self):
        return_msg = {}
        item = get_item(self.port, self.state)
        if item['highest bid'][1] == 'No bids yet':
            return_msg.update(self.not_sold())
        else:  # send out sold to all and win to only the winning client
            # self.winning_bid(item)
            return_msg.update(self.sold_to(item))
        self.send_all_clients.append(return_msg)

    def sold_to(self, item):
        highest_bid = get_highest_bid(item)
        highest_bidder = get_highest_bidder(item)
        client = get_client(highest_bidder, self.state)
        msg = {
            'type': self.BID_SOLDTO,
            'item #': self.item_number,
            'name': client['name'],
            'ip address': client['ip'],
            'port #': client['port'],
            'amount': highest_bid
        }
        return msg

    def not_sold(self):
        msg = {
            'type': self.BID_NOTSOLD,
            'item #': self.item_number,
            'reason': 'No valid bid made'
        }
        return msg


