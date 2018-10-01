from udp_server import UDPServer

state = {'names': []}
host = "192.168.0.106"  # todo socket.gethostname() doesn't work? Do we need to get hostnames programmatically?
port = 5023

udp_server = UDPServer(host=host, port=port, state=state)
udp_server.start()

