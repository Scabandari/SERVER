import json
import ast


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
        print("State's type: {}".format(type(state)))
        print(state)
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











