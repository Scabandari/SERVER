import threading
from time import sleep
import socket
from client_connection import ClientConnection


"""We have a TCPServer for each item on bid, self.connection_list[] is a list of bidders ie clients
    who have successfully connected over tcp to ip + port for specific item on bid. """


class TCPServer(threading.Thread):
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
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((host, port))
        self.tcp_socket.listen(5)
        threading.Thread.__init__(self)

    def run(self):
        print("TCP connection started on server side")
        send_all_clients = threading.Thread(target=self.check_all_clients)
        send_all_clients.start()
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
            newthread = ClientConnection(addr[0], addr[1], conn, self.state, self.state_lock, self.txt_file)
            newthread.start()
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
                    client.send_msg(all_clients_msg)
            sleep(0.2)  # sleep 200 millis and make sure others can easily acquire all_clients_lock

    
    
    def bidding(self, msg):
        
        print("Bid")
    
    



    def highest_bid(self):
        print("highest Bid")





    def winning_bid(self):
        print("winning bid")




    def bid_over(self):
        print("Bid Over")
    

    def sold_to(self):
        print("Sold to")

    
    def not_sold(self):
        print("Not Sold")


