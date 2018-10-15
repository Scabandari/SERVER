import threading
from udp_server import UDPServer
from tcp_server import TCPServer

# todo TCP working both on same machine, test w/ client on other laptop

state = {'names': []}
host = "192.168.0.107"  # todo socket.gethostname() doesn't work? Do we need to get hostnames programmatically?
port = 5023
state_lock = threading.Lock()

udp_server = UDPServer(host=host, port=port, state=state, state_lock=state_lock)

tcp_port = 5001
tcp_server = TCPServer(host=host, port=tcp_port, state=state, state_lock=state_lock)

udp_server.start()
tcp_server.start()

