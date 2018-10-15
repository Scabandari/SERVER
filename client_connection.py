import socket
import threading
#from SocketServer import ThreadingMixIn

# referenced here: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


class ClientConnection(threading.Thread):
    def __init__(self, ip, port, connection, state, state_lock):
        self.ip = ip
        self.port = port
        self.connection = connection
        self.state = state
        self.state_lock = state_lock
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
            print("Connection from user: " + data)
            self.connection.send("Successful response over tcp".encode('ascii'))
