import json
from pathlib import Path



# todo STATE MUST BE PROTECTED BY A LOCK WHEN THREADING


def update_txt_file():
    pass
    #     pass  # todo rea
    # else:
    #     pass  # todo create file and write state to it


def dict_to_bytes(dict_):
    json_str = json.dumps(dict_)
    bytes_ = json_str.encode('utf-8')  # todo: was ascii
    return bytes_


def check_name(name, state):
    """this functions takes the name for a registration and checks to see
        that name is available for registration if so return True else
        return False"""
    for n in state['names']:
        if n[0] == name:
            return False
    return True


# def ack_register_attempt(msg_received, socket_, return_address, state):
#     """this function should return a msg to the sender that the registration is successful or not
#         and if so update internal state to reflect that as well as update the .txt file"""
#     # todo make sure the name isn't already registered
#     # todo some type checking for port numbers and ip addresses would be good
#     # todo check that someone isn't already registered w/ that name
#     name = msg_received['name']
#     ip = msg_received['ip']
#     response = msg_received
#     request_number = msg_received['request']
#     print("Received request#: {} from: {} @ address: {}".format(name, ip, request_number))
#
#     if check_name(name, state):
#         state['names'].append((name, ip))
#         print("{} registration acknowledged".format(name))
#         response['type'] = REGISTERED
#     else:
#         print("{} registration not acknowledged. Duplicate names".format(name))
#         response = {'request': request_number, 'type': UNREGISTERED, 'reason': 'Duplicate name'}
#     response = dict_to_bytes(response)
#     socket_.sendto(response, return_address)


# def handle_response(msg_received, socket_, return_address, state):
#     """This functions accepts the incoming dict and checks the type so it
#         can call the corresponding ack function. If this function can't identify
#         the proper type it will return a string of the error msg"""
#     if msg_received['type'] == REGISTER:
#         ack_register_attempt(msg_received, socket_, return_address, state)
#     else:
#         print("type != Register threfore do nothing")  # todo change this








