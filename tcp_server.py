import threading
import socket
from client_connection import ClientConnection


class TCPServer(threading.Thread):
    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state, state_lock, txt_file):
        self.host = host
        self.port = port
        self.state = state
        self.txt_file = txt_file
        self.state_lock = state_lock  # locks access to state, update .txt file while lock held
        self.connection_list = []
        self.messages = []  # list of msg's or dicts sent from clients over tcp
        self.continue_thread = True  # set to False if we want to terminate thread
#        self.add_connections_thread = threading.Thread(target=self.add_connections)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((host, port))
        self.tcp_socket.listen(5)
        threading.Thread.__init__(self)

    def run(self):
        print("TCP connection started on server side.")
        while self.continue_thread:
            # (conn, (ip, port)) = self.tcp_socket.accept()
            (conn, addr) = self.tcp_socket.accept()
            print("TCP connection from ip: {} port: {}".format(str(addr[0]), str(addr[1])))

            # tcp_connection = threading.Thread(target=self.connection_thread, args=(conn, addr))
            # tcp_connection.start()
            # self.connection_list.append(tcp_connection)

            newthread = ClientConnection(addr[0], addr[1], conn, self.state, self.state_lock, self.txt_file)
            newthread.start()
            self.connection_list.append(newthread)

    # @staticmethod
    # def connection_thread(connection, address):
    #     """Every client is connected through a connection_thread"""
    #     while True:
    #         # data = connection.recv(1024).decode('ascii')
    #         data = connection.recv(1024).decode('utf-8')
    #         if not data:
    #             print("Data is not correct")
    #             break
    #         print("Connection from user: " + data)
    #         connection.send("Successful response over tcp".encode('ascii'))
