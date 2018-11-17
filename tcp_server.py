import threading
from time import sleep
import socket
import ast
from client_connection import ClientConnection, all_client_messages


"""We have a TCPServer for each item on bid, self.connection_list[] is a list of bidders ie clients
    who have successfully connected over tcp to ip + port for specific item on bid. """


class TCPServer(threading.Thread):
    HIGHEST = 'HIGHEST'

    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state, state_lock, txt_file):
        self.host = host
        self.port = port
        self.state = state
        self.txt_file = txt_file
        self.send_all_clients = []
        self.all_clients_lock = threading.Lock()
        self.state_lock = state_lock  # locks access to state, update .txt file while lock held
        self.connection_list = []
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


    def winning_bid(self):
        print("winning bid")


    def bid_over(self):
        print("Bid Over")
    

    def sold_to(self):
        print("Sold to")

    
    def not_sold(self):
        print("Not Sold")


