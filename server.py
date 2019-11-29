import socket
import select

Header_Length = 10

IP = "127.0.0.1"
PORT = 1234

class Channels(object):
	def __init__(self, name):
		self.name = name
		self.members = set()

	def AddUserToChannel(self, client):
		if client not in members:
			self.members.add(client)
		else:
			print "Member exists"

	def RemoveUserFromChannel(self, client):
		self.members.discard(client)
		

# Creating socket with IPv4 and TCP
Server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setting server socket option
Server_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Server will use IP and PORT to connect
Server_Socket.bind((IP, PORT))

# Start listening
Server_Socket.listen()

# List of sockets
Sockets_List = [Server_Socket]

# Using dictonary to create client list
Clients = {}

print(f'Listening for connections on {IP}:{PORT}')

# Recevie message
def receive_message(Client_Socket):

	try:
		# Checking message length
		Message_Header = Client_Socket.recv(Header_Length)

		if not len(Message_Header):
			return False

		Message_Length = int(Message_Header.decode('utf-8'))

		# Return header and data
		return {'header': Message_Header, 'data': Client_Socket.recv(Message_Length)}
	
	except:
		return False



while True:
	Read_Sockets, _, Exception_Sockets = select.select(Sockets_List, [], Sockets_List)

	# Checking all sockets
	for Connected_Socket in Read_Sockets:

		# Checking new connection
		if Connected_Socket == Server_Socket:
			Client_Socket, Client_Address = Server_Socket.accept() # Accepting new connection
			
			# Get username provided by the client
			User = receive_message(Client_Socket)

			# Client disconnect
			if User is False:
				continue

			# If client did not disconnect, appending the connected list
			Sockets_List.append(Client_Socket)
			Clients[Client_Socket] = User

			print('Accepted new connection from {}:{}, username:{}'.format(*Client_Address, User['data'].decode('utf-8')))

		# Old connection
		else:
			# New message
			Message = receive_message(Connected_Socket)

			# Remove client from the list if disconnect
			if Message is False:
				print('Closed connection from:{}'.format(Clients[Connected_Socket]['data'].decode('utf-8')))
				Sockets_List.remove(Connected_Socket)
				del Clients[Connected_Socket]
				continue

			# Checking who sent the message
			User =  Clients[Connected_Socket]

			print(f'Received message from {User["data"].decode("utf-8")}: {Message["data"].decode("utf-8")}')

			# Broadcasting message
			for Client_Socket in Clients:
				# Filtering so that sender do not receive the message
				if Client_Socket != Connected_Socket:
					Client_Socket.send(User['header'] + User['data'] + Message['header'] + Message['data'])

	# Exception handling
	for Connected_Socket in Exception_Sockets:
		Sockets_List.remove(Connected_Socket)
		del Clients[Connected_Socket]	
