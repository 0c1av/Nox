import socket

def run():
	s = socket.socket()
	s.bind(('', 0))
	port = s.getsockname()[1]
	s.close()
	return port
