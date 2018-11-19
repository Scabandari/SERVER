import threading
from udp_server import UDPServer
from tcp_server import TCPServer

TEXT_FILE = 'state.txt'
state = {'clients': [],  # list of dicts: name, ip, port
         'items': []  # list of dicts: description, min bid, seller, highest bid, open status
         }

"""  for items above
       item = {
            'description': msg['description'],
            'minimum bid': msg['minimum bid'],
            'seller': msg['name'],
            'highest bid': (msg['minimum bid'], None),
            'open status': True,
            'starting time': time.time(),
            'port #': self.item_port
        }
"""
AUCTION_TIME = 300  # number of seconds items should be up for bid
#ipadd = input("Please Enter host IP address: ")
ipadd = "192.168.1.12"
#host = ipadd
host = '192.168.0.107'
udp_port = 5024
tcp_port = 5002
state_lock = threading.Lock()
#send_all_clients = []  # msg queue for msg's that need to be sent to all clients
#all_clients_lock = threading.Lock()

# todo we need a seperate thread to go through all the items in state['items open']
# todo and check if their time is up (start time + 300=5min), if so change item['open status'] to False and
# todo ass to items closed list, remove from items opened, send msg to all bidders about winner etc.

udp_server = UDPServer(
    host=host,
    port=udp_port,
    state=state,
    state_lock=state_lock,
    txt_file=TEXT_FILE
)
"""
tcp_server = TCPServer(
    host=host,
    port=tcp_port,
    state=state,
    state_lock=state_lock,
    txt_file=TEXT_FILE
)
"""
udp_server.start()
#tcp_server.start()

