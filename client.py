import socket
import select
import errno
import sys

Header_Length = 10

IP = "127.0.0.1"
PORT = 1234
Client_Username = input("Username: ")


# Creating socket for client
Client_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client_Socket.connect((IP, PORT))
Client_Socket.setblocking(False)

# Sending username and header
Username = Client_Username.encode('utf-8')
Username_Header = f"{len(Username):^{Header_Length}}".encode('utf-8')
Client_Socket.send(Username_Header + Username)

while True:
	# Waiting for message input
	Message = input(f'{Client_Username} >>> ')
	#Message = ""

	# Sending message
	if Message:
		Message = Message.encode('utf-8')
		Message_Header = f"{len(Message):^{Header_Length}}".encode('utf-8')
		Client_Socket.send(Message_Header + Message)

	# Checking for received messages from other users
	try:

		while True:
			Username_Header = Client_Socket.recv(Header_Length)

			# Closing connection
			if not len(Username_Header):
				print('Server Disconnected')
				sys.exit()

			# Decoding username and message
			Username_Length = int(Username_Header.decode('utf-8'))
			Username = Client_Socket.recv(Username_Length).decode('utf-8')
			Message_Header = Client_Socket.recv(Header_Length)
			Message_Length = int(Message_Header.decode('utf-8'))
			Message = Client_Socket.recv(Message_Length).decode('utf-8')

			print(f'{Username} >>> {Message}')

	# Error handling
	except IOError as ex:
		if ex.errno != errno.EAGAIN and ex.errno != errno.EWOULDBLOCK:
			print('IO Error: {}'.format(str(ex)))
			sys.exit()
		continue
	# Error handling
	except Exception as ex:
		print('Error: '.format(str(e)))
		sys.exit()