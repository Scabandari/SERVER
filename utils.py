import json
import ast
import ipaddress


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
    #print("\nupdate_txt_file() running\n")
    file_name = file_name
    state_ = str(state)
    with open(file_name, 'w') as txt_file:
        txt_file.write(state_)


def recover_state(file_name):
    with open(file_name, 'r') as my_file:
        data = my_file.read()
        state = ast.literal_eval(data)
        #print("State's type: {}".format(type(state)))
        #print(state)
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
    for item in state['items open']:
        if name == item['highest bid'][1]:
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
    for item in state['items open']:
        if item['seller'] == name:
            return True
    return False


def under_three_opens(name, state):
    """If adding another item for bid would give the client with this name more
        than 3 items up for bid return true, else false"""
    counter = 0
    for item in state['items open']:
        if item['seller'] == name:
            counter += 1
    return counter < 3

def get_item_descriptions(state):
    list_of_items = {}
    for items in state["items open"]:
        # copying highest bid + highest bidder name below so that i change the highest bidder value to empty string
        # if its value is None. This is to avoid conversion errors from using the ast library
        high_bid_plus_bidder = items['highest bid']
        if high_bid_plus_bidder[1] is None:
            high_bid_plus_bidder[1] == 'no one'
        msg = {
            'description:': items['description'],
            'minimum bid:': items['minimum bid'],
            'highest bid:': high_bid_plus_bidder,
            'port #': items['port #']
        }
        list_of_items.update(msg)
    return list_of_items


def get_item(portNumber, state):
    item_for_bid = {}
    for items in state['items open']:
        if items['port #'] == portNumber:
            item_for_bid.update(items)
    return item_for_bid

# Function below won't work yet because the port associated with the client connection is
# not the port nb associated with the client in the state file

def get_bidder_name(portNumber,state):
    bidder_name = ""
    for client in state['clients']:
        if client['port'] == portNumber:
            bidder_name = client['name']
    return bidder_name


def get_highest_bid(item):
    max_bid_plus_client= item['highest bid']
    return_value = max_bid_plus_client[0]
    return return_value







