import threading
import socket
from client_connection import ClientConnection


class TCPServer(threading.Thread):
    # state will be a dict in main.py must be backed up in .txt file
    def __init__(self, host, port, state):
        self.host = host
        self.port = port
        self.state = state
        self.connection_list = []
        self.continue_thread = True  # set to False if we want to terminate thread
#        self.add_connections_thread = threading.Thread(target=self.add_connections)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((host, port))
        self.tcp_socket.listen(5)
        threading.Thread.__init__(self)

    def run(self):
        #self.add_connections_thread.start()
        #self.tcp_socket.listen(5)
        print("TCP connection started on server side.")
        while self.continue_thread:
            (conn, (ip, port)) = self.tcp_socket.accept()
            print("TCP connection from ip: {} port: {}".format(str(ip), str(port)))
            #tcp_connection = threading.Thread(target=self.connection_thread, args=(conn, addr))
            #tcp_connection.start()
            #self.connection_list.append(tcp_connection)
            newthread = ClientConnection(ip, port, conn)
            newthread.start()
            self.connection_list.append(newthread)

            # data = conn.recv(1024).decode('ascii')
            # if not data:
            #     print("Data is not correct")
            #     break
            # print("Connection from user: " + data)
            # conn.send("Successful response over tcp".encode('ascii'))

    # def add_connections(self):
    #     while True:
    #         self.tcp_socket.listen(5)
    #         conn, addr = self.tcp_socket.accept()
    #         print("TCP connection from {}".format(str(addr)))
    #
    #
    @staticmethod
    def connection_thread(connection, address):
        """Every client is connected through a connection_thread"""
        while True:
            data = connection.recv(1024).decode('ascii')
            if not data:
                print("Data is not correct")
                break
            print("Connection from user: " + data)
            connection.send("Successful response over tcp".encode('ascii'))


