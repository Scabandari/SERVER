import json
import ast
import ipaddress
import os

def client_connected(ip_port, connection_list):
    """
    :param ip_port: a tuple (ip, port)
    :param connection_list: list of connections ie [(ip, port), (ip, port)]
    :return: True if there is already a connection w/ the given ip and port
    """
    for connection in connection_list:
        if ip_port[0] == connection[0] and ip_port[1] == connection[1]:
            return True
    return False


def is_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return_val = True
    except ValueError:
        return_val = False
    return return_val


def update_txt_file(state, file_name):
    # print("\nupdate_txt_file() running\n")
    file_name = file_name
    state_ = str(state)
    with open(file_name, 'w') as txt_file:
        txt_file.write(state_)


def attempt_recover(text_file):
    # if os.stat(text_file) == 0:
    #     state = {'clients': [], 'items': [], 'udp_connections': []}
    #     udp_conns = None
    #     server_crashed = False
    # else:
    #     state = recover_state(text_file)
    #     udp_conns = state['udp_connections']
    #     server_crashed = True
    # return state, udp_conns, server_crashed
    if os.path.getsize(text_file) > 0:
        next_item = 1
        state = recover_state(text_file)
        for item in state['items']:
            item['open status'] = 0
            if item['item #'] >= next_item:
                next_item = item['item #'] + 1
        udp_conns = state['udp_connections']
        server_crashed = True

    else:
        next_item = None
        state = {'clients': [], 'items': [], 'udp_connections': []}
        udp_conns = None
        server_crashed = False
    return state, udp_conns, server_crashed, next_item



# # # attempt_recover takes the text file, udp_connections, and state
# # # if needs to recover upd_connections = what's in state.txt
# # # state = recover_state
# state_lock = threading.Lock()
# state = {'clients': [],  # list of dicts: name, ip, port
#          'items': [],  # list of dicts: description, min bid, seller, highest bid, open status
#          'udp_connections': []
#          }
# attempt_recover(TEXT_FILE, udp_connections, state, state_lock)


def recover_state(file_name):
    with open(file_name, 'r') as my_file:
        data = my_file.read()
        state = ast.literal_eval(data)
        # print("State's type: {}".format(type(state)))
        # print(state)
        return state


def dict_to_bytes(dict_):
    json_str = json.dumps(dict_)
    bytes_ = json_str.encode('utf-8')  # todo: was ascii
    return bytes_


def bytes_to_dict(bytes_):
    pass


def top_bidder(name, state):
    """this functions takes a name and returns true if that client is the
        top bidder on any open items for bid"""
    for item in state['items']:
        if item['open status'] is True and name == item['highest bid'][1]:
            return True
    return False


""" state looks like...
    {
    'items closed': [], 
    'items open': [{'minimum bid': 10, 
                    'starting time': 1539884389.5983984, 
                    'seller': 'ryan', 'description': 'bat', 
                    'highest bid': (10, None),
                    'open status': True}], 
    'clients': [{'name': 'ryan', 'ip': '192.168.0.107', 'port': 5000}]}
"""


def name_registered(name, state):
    """this functions takes the name for a registration and checks to see
        that name is already registered"""
    for client in state['clients']:
        if client['name'] == name:
            return True
    return False


def name_matches_ip(name, ip,  state):
    """Given a name and IP this checks if that name and ip are listed together or registered
        together in state under clients. Returns false also if cannot find name registered"""
    for client in state['clients']:
        if client['name'] == name:
            if client['ip'] == ip:
                return True
            else:
                return False
    return False


def has_open_items(name, state):
    """If the client with this name has items open for bid return True"""
    for item in state['items']:
        if item['open status'] is 1 and item['seller'] == name:
            return True
    return False


def under_three_opens(name, state):
    """If adding another item for bid would give the client with this name more
        than 3 items up for bid return true, else false"""
    counter = 0
    for item in state['items']:
        if item['seller'] == name:
            counter += 1
    return counter < 3


def get_item_descriptions(state):
    list_of_items = {}
    for items in state["items"]:
        if items['open status'] == 1:
            # copying highest bid + highest bidder name below so that i change the highest bidder value to empty string
            # if its value is None. This is to avoid conversion errors from using the ast library
            high_bid_plus_bidder = items['highest bid']
            list_version = list(high_bid_plus_bidder)  # because tuples are immutable
            if list_version[1] is None:
                list_version[1] = 'no one'
            high_bid_plus_bidder = tuple(list_version)
            msg = {
                'description:': items['description'],
                'minimum bid:': items['minimum bid'],
                'highest bid:': high_bid_plus_bidder,
                'port #': items['port #']
            }
            list_of_items.update(msg)
    return list_of_items
# def getItem(portNumber,state):
#     #port = int(portNumber)
#     itemForBid = {}
#     for items in state['items']:
#         if items['port #'] == portNumber:
#             itemForBid.update(items)
#     return itemForBid


def get_item(port_number, state):
    item_for_bid = {}
    for items in state['items']:
        if items['open status'] == 1:
            if items['port #'] == port_number:
                item_for_bid.update(items)
    return item_for_bid

# Function below won't work yet because the port associated with the client connection is
# not the port nb associated with the client in the state file


def get_bidder_name(port_number, state):
    bidder_name = ""
    for client in state['clients']:
        if client['port'] == port_number:
            bidder_name = client['name']
    return bidder_name


def get_highest_bid(item):
    max_bid_plus_client = item['highest bid']
    highest_bid = max_bid_plus_client[0]
    return highest_bid


def get_highest_bidder(item):
    max_bid_plus_client = item['highest bid']
    highest_bidder = max_bid_plus_client[1]
    return highest_bidder


def get_client(name, state):
    for client in state['clients']:
        if client['name'] == name:
            return client
        else:
            return "Could not locate client"







