import threading
from udp_server import UDPServer
from tcp_server import TCPServer

# todo TCP working both on same machine, test w/ client on other laptop
TEXT_FILE = 'state.txt'
state = {'clients': [],  # list of dicts: name, ip, port
         'items open': [],  # list of dicts: description, min bid, seller, highest bid, open status
         'items closed': []}  # list of dicts: description, min bid, seller, highest bid, open status
host = "192.168.0.107"  # todo socket.gethostname() doesn't work? Do we need to get hostnames programmatically?
udp_port = 5024
state_lock = threading.Lock()

# todo we need a seperate thread to go through all the items in state['items open']
# todo and check if their time is up (start time + 300=5min), if so change item['open status'] to False and
# todo to items closed list, remove from items opened

udp_server = UDPServer(
    host=host,
    port=udp_port,
    state=state,
    state_lock=state_lock,
    txt_file=TEXT_FILE)

tcp_port = 5002
tcp_server = TCPServer(
    host=host,
    port=tcp_port,
    state=state,
    state_lock=state_lock,
    txt_file=TEXT_FILE)

udp_server.start()
tcp_server.start()

