import json

REGISTER = 'REGISTER'
REGISTERED = 'REGISTERED'


def dict_to_bytes(dict_):
    json_str = json.dumps(dict_)
    bytes_ = json_str.encode('utf-8')  # todo: was ascii
    return bytes_


def send_back_response(response, socket_, return_address):
    socket_.sendto(response,  return_address)


def ack_register(msg_received, socket_, return_address):
    """this function should return a msg to the sender that the registration is successful or not
        and if so update internal state to reflect that as well as update the .txt file"""
    # todo make sure the name isn't already registered
    # todo some type checking for port numbers and ip addresses would be good
    print("{} registration acknowledged".format(msg_received['name']))
    response = msg_received
    response['type'] = REGISTERED
    response = dict_to_bytes(response)
    send_back_response(response, socket_, return_address)


def handle_response(msg_received, socket_, return_address):
    """This functions accepts the incoming dict and checks the type so it
        can call the corresponding ack function. If this function can't identify
        the proper type it will return a string of the error msg"""
    if msg_received['type'] == REGISTER:
        ack_register(msg_received, socket_, return_address)

    else:
        print('msg_received[type] not REGISTER')
        print(msg_received)
        return None  # todo this should return a not acked if it didn't work


def send_back_error(error_msg):
    pass





