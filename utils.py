import json
import ast
from pathlib import Path


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


def bytes_to_dict(bytes):
    pass


def check_name(name, state):
    """this functions takes the name for a registration and checks to see
        that name is available for registration if so return True else
        return False"""
    for client in state['clients']:
        if client['name'] == name:
            return False
    return True










