import socket
import threading
#from SocketServer import ThreadingMixIn

# referenced here: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


class ClientConnection(threading.Thread):
    def __init__(self, ip, port, connection):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.connection = connection
        print("Starting tcp socket connection with client at " + str(ip) + " port " + str(port))

    def run(self):
        while True:
            data = self.connection.recv(1024)
            if data:
                print("Server received data: " + str(data))
