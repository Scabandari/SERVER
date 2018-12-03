import threading
from udp_server import UDPServer
from tcp_server import TCPServer
from utils import attempt_recover

TEXT_FILE = 'state.txt'
#udp_connections = None

# # attempt_recover takes the text file, udp_connections, and state
# # if needs to recover upd_connections = what's in state.txt
# # state = recover_state
state_lock = threading.Lock()
# state = {'clients': [],  # list of dicts: name, ip, port
#          'items': [],  # list of dicts: description, min bid, seller, highest bid, open status
#          'udp_connections': []
#          }
with state_lock:
    state, udp_connections, server_crashed, next_item = attempt_recover(TEXT_FILE)

crashed_msg = None
if server_crashed:  # state reset = False means a fresh start and no recovery
    msg = "Our server seems to have crashed.\nAny items not previously awarded\nto a winner must be resubmitted\n\n"
    crashed_msg = {
                'type': 'SERVER-CRASHED',
                'description': msg
            }
    # todo SEND MSG TO ALL CLIENTS NOTIFYING OF SERVER CRASH

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
AUCTION_TIME = 30 # 60   #300  # number of seconds items should be up for bid
#ipadd = input("Please Enter host IP address: ")
ipadd = "172.31.5.102"
#host = ipadd

#host = '192.168.0.106'
host = '192.168.0.106 '


udp_port = 5024
tcp_port = 5002

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
    txt_file=TEXT_FILE,
    udp_connections=udp_connections,
    server_crashed_msg=crashed_msg,
    next_item=next_item
)

udp_server.start()

