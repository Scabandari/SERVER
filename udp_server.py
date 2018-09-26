import socket
import ast
from utils import handle_response


#choices = [REGISTER]
clients = []

# UDP server

host = "192.168.0.105"  # todo socket.gethostname() doesn't work?
port = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
print("Server started.")
while True:
    data, addr = s.recvfrom(1024)
    data = data.decode('ascii')  #data.decode('utf-8')
    msg_received = ast.literal_eval(data)  # unpacked as a dict object
    handle_response(msg_received, s, addr)

    # print("Client sent: {}".format(data))
    # if unpacked_dict['type'] is REGISTER:
    #     print("client registered. Responding to address: ".format(addr))
    #     s.sendto("Registration Successful".encode('utf-8'), addr)
    # todo check which kind of message has been sent based on it's type and act accordingly


# data, addr = s.recvfrom(1024)
# data = data.decode('utf-8')
# #unpacked_dict = ast.literal_eval(data)
# print("Client sent: {}".format(data))
# s.sendto("Message received".encode('utf-8'), addr)

s.close()