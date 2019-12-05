import os
import select
import socket
import string
import sys




"""
This function is taken from the following source:

https://github.com/jrosdahl/miniircd/blob/master/miniircd
"""
def buffer_to_socket(msg):
	return msg.encode()

"""
This function is taken from the following source:

https://github.com/jrosdahl/miniircd/blob/master/miniircd
"""
def socket_to_buffer(buf):
	return buf.decode(errors="ignore")








###################################### CHANNEL CLASS START ######################################################

"""

Handle all channel activities

"""
class Channel(object):

	# constructor
	def __init__(self, server, name):
		print("Creating channel with name " + name)
		self.server = server
		self.name = name
		self.members = set() # initializing with no members

	# add member to a existing channel
	def addMember(self, client):
		print(sys._getframe().f_code.co_name)
		self.members.add(client)


	# remove member from a existing channel and if last member leave the channel the channel delete itself
	def removeClient(self, client):
		print(sys._getframe().f_code.co_name)
		self.members.discard(client)
		if not self.members: # remove the channel if no members left on the channel
			client.server.removeChannel(self)
	



############################################## CHANNEL CLASS END ####################################################




############################################## CLIENT CLASS START ###################################################################

"""

Handle all client activities

"""
class Client(object):

	# constructor
	def __init__(self, server, socket):
		print(__name__ + " client")
		self.server = server
		self.socket = socket
		self.channels = {}   # stores all the channel names the client joins
		self.nickname = None
		self.user = None
		self.realname = None

		self.host, self.port = socket.getpeername() # get host and port of the client

		self.readbuffer = ""     # initialize empty readbuffer
		self.writebuffer = ""    # initialize empty witebuffer
	
	
	# returns client information
	def get_prefix(self):
		print(sys._getframe().f_code.co_name)
		return "%s!%s@%s" % (self.nickname, self.user, self.host)
	prefix = property(get_prefix)


	# returns the size of writebuffer
	def write(self):
		return len(self.writebuffer)


	# read user inputs and check for commands and arguments
	def read(self):
		print(sys._getframe().f_code.co_name)
		lines = self.readbuffer
		self.readbuffer = lines[-1]
		lines = lines[:-1]
		print(lines)
		for line in lines.split('\r\n'): # splits the input from the user
			print(line)
			if not line:
				continue
			x = line.split(" ", 1)
			command = x[0]  # storing the command from user
			
			if len(x) == 1:
				arguments = []
			else:
				if len(x[1]) > 0 and x[1][0] == ":":
					arguments = [x[1][1:]]   # storing the command arguments from the user
				else:
					y = x[1].split(" :", 1)
					arguments = y[0].split() # spliting arguments to check if there more than one argument exists
					if len(y) == 2:
						arguments.append(y[1])
				print(command)
				print(arguments)
				self.handleCommand(command, arguments) # handling the user command and arguments
				

	# write given message to the writebuffer
	def message(self, msg):
		print(sys._getframe().f_code.co_name)
		print("client: ", self.user, " @ ", self.host)
		self.writebuffer += msg + "\r\n" # writing to the buffer


	# handle all the user commands and take actions according to the given command
	def handleCommand(self, command, arguments):

		# IRC USER command handler
		def USER():
			print("User handler")
			if len(arguments) < 4:
				self.message("Not enough parameters")
			print(arguments)
			self.user = arguments[0]
			self.realname = arguments[3].split('\r')[0]
			server.clients[self.socket]
			if self.user and self.nickname:
				initconfirmMessage = ":" + server.name + " 001 " + self.nickname + " :Welcome to IRC Server"
				self.message(initconfirmMessage)
				pt2confirmMessage = ":" + server.name + " 002 " + self.nickname + " :Host is " + server.name + ", running IRC we made"
				self.message(pt2confirmMessage)
				pt3confirmMessage = ":" + server.name + " 003 " + self.nickname + " :Server was made sometime"
				self.message(pt3confirmMessage)


		# IRC NICK command handler
		def NICK():
			print("Nick handler")
			if len(arguments) < 1:
				self.message("Not enough parameters")
			print(arguments)
			if self.server.matchNickname(arguments[0]):
				disconMsg = ":%s 433 %s :Nickname already in use" % (self.server.name, arguments[0])
				self.message(disconMsg)
				self.socket.close() # close the client's socket
				del self.server.clients[self.socket]
				# self.disconnect(disconMsg)
				return
			self.nickname = arguments[0]
			print("Nickname set to " + self.nickname)

		# IRC JOIN command handler
		def JOIN():
			print("JOIN")
			if len(arguments) < 1:
				self.message("Not enough parameter")
				return
			print("Argument 0 = " + arguments[0])
			joined = False
			for channelname, channel in server.channels.items():
				if channelname == arguments[0]:
					print("Join existing channel")
					self.joinChannel(channel)
					joined = True
			if not joined:
				print("Join new channel")
				server.channels[arguments[0]] = Channel(self, arguments[0])
				self.joinChannel(server.channels[arguments[0]])

		# IRC PRIVMSG command handler
		def PRIVMSG():
			targetname = arguments[0]
			message = arguments[1]
			print("Targetname = " + targetname)
			client = server.findClient(targetname)
			print("Client returned = %s", client)
			if server.hasChannel(targetname):
				print("Send to channel")
				channel = server.getChannel(targetname)
				self.messageToChannel(channel, command, "%s :%s" % (channel.name, message))
			elif client:
				print("PM to user")
				prefix = self.prefix
				print("Prefix: ", prefix, " command: ", command, " target: ", targetname, " message: ", message)
				messageToSend = ":%s %s %s :%s" % (prefix, command, targetname, message)
				print(messageToSend)
				client.message(messageToSend)

		# IRC PART command handler
		def PART():
			if len(arguments) > 1:
				partmsg = arguments[1]
			else:
				partmsg = self.nickname
			for channelname in arguments[0].split(","):
				if channelname:
					if channelname in self.channels:
						channel = self.channels[irc_lower(channelname)]
						self.messageToChannel(channel, "PART", "%s :%s" % (channelname, partmsg), True)
						del self.channels[irc_lower(channelname)]
						server.removeMemberFromChannel(self, channelname)

		# IRC QUIT command handler
		def QUIT():
			if len(arguments) < 1:
				quitmsg = self.nickname
			else:
				quitmsg = arguments[0]
			self.disconnect(quitmsg)

		# table to look which function to call for what command
		handler_table = {"USER": USER, "NICK": NICK, "JOIN": JOIN, "PRIVMSG": PRIVMSG, "PART": PART, "QUIT": QUIT}
		server = self.server
		try:
			print("start of command handler")
			if '\n' in command:
				command = command.split('\n')[1]
			print("command = " + command)
			handler = handler_table.get(command) # calling appropiate function
			if handler:
				handler()
		except KeyError:
			self.message("Unknown Command")

	# disconnect a client from the server
	def disconnect(self, quitmsg):
		messageToSend = ":%s %s" % (self.prefix, quitmsg)
		self.message(messageToSend) # printing the quit message if provided
		self.server.printInformation("Disconnected connection from %s" % self.host)
		self.socket.close() # close the client's socket
		self.server.removeClient(self, quitmsg) # removing client from the server class

	# deliver message to a channel
	def messageToChannel(self, channel, command, message, include_self=False):
		print("message channel")
		line = ":%s %s %s" % (self.prefix, command, message)
		print(line)
		for client in channel.members:
			if client != self or include_self: # making sure the sender do not get the message
				client.message(line)


	# read incoming information using readbuffer
	def readNotification(self):
		print(sys._getframe().f_code.co_name)
		try:
			data = self.socket.recv(2048) # receving stream of data
			quitmsg = "EOT"
		except socket.error as x:
			data = ""
			quitmsg = x

		if data:
			self.readbuffer += socket_to_buffer(data)
			self.read()
		else:
			self.disconnect(quitmsg) # diconnect client if something goes wrong


	# write outgoing information using writebuffer
	def writeNotification(self):
		print(sys._getframe().f_code.co_name)
		try:
			sent = self.socket.send(buffer_to_socket(self.writebuffer))
			self.writebuffer = self.writebuffer[sent:]
		except socket.error as x:
			self.disconnect(x) # disconnect client if exception happens


	# let user join a particular channel
	def joinChannel(self, channelToJoin):
		print("in join channel")
		channelToJoin.addMember(self) # add client to the channel class
		self.channels[channelToJoin.name] = channelToJoin # adding channel name to the client class
		self.messageToChannel(channelToJoin, "JOIN", channelToJoin.name, True)
		whoinMsg = ":" + self.server.name + " 353 " + self.nickname + " = " + channelToJoin.name
		for member in channelToJoin.members:
			whoinMsg += " " + member.nickname
		self.message(whoinMsg)
		endNameMsg = ":" + self.server.name + " 366 " + self.nickname + " " + channelToJoin.name + " :End of NAMES list"
		self.message(endNameMsg)



######################################################## CLIENT CLASS END #####################################################################




######################################################## SERVER CLASS START ##############################################################################

"""

Handle all server activities

"""
class Server(object):

	# constructor
	def __init__(self):
		self.address = ""
		self.name = socket.getfqdn(self.address)[:63]
		self.channels = {} # stores all the existing channels
		self.clients = {}  # stores all the existing clients
		self.nicknames = {} # stores all the nicknames of the clients

	# find existing client using the nickname
	def findClient(self, nickname):
		for client in self.clients.values():
			if client.nickname == nickname:
				return client

	# return True if a channel exists, otherwise return False
	def hasChannel(self, name):
		return irc_lower(name) in self.channels

	# return channel object if exists
	def getChannel(self, channelname):
		if irc_lower(channelname) in self.channels:
			channel = self.channels[irc_lower(channelname)]
		else:
			channel = Channel(self, channelname)
			self.channels[irc_lower(channelname)] = channel
		return channel

	# remove a client from a existing channel
	def removeMemberFromChannel(self, client, channelname):
		if irc_lower(channelname) in self.channels:
			channel = self.channels[irc_lower(channelname)]
			channel.removeClient(client)

	# help removeMemberFromChannel() to remove a client from the channel
	def removeClient(self, client, quitmsg):
		client.message(":%s QUIT :%s" % (client.prefix, quitmsg))
		for x in client.channels.values():
			client.messageToChannel(x, "QUIT", quitmsg)
			self.removeMemberFromChannel(client, x.name)
		del self.clients[client.socket]

	# delete a channel from the server
	def removeChannel(self, channel):
		del self.channels[irc_lower(channel.name)]

	# print information with provided message
	def printInformation(self, msg):
		print(msg)
		sys.stdout.flush()

	# preparing server by creating sockets
	def start(self):
		# creating sockets
		serversockets = []
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		port = 6667

		# bind sockets, if fail close the server
		try:
			s.bind((self.address, port))
		except:
			print ("Cannot bind")
			sys.exit(1)

		s.listen()
		serversockets.append(s)
		del s
		print(f"Listening for connections on :{port}")
		self.run(serversockets) # run the server


	def matchNickname(self, nick):
		for x in self.clients.values():
			if x.nickname == nick:
				return True
		return False

	# let the server run by checking any incoming requests
	def run(self, serversockets):
		while True:
			# reading sockets to check incoming and existing socket connection
			(iwtd, owtd, ewtd) = select.select(serversockets + [x.socket for x in self.clients.values()], [x.socket for x in self.clients.values() if x.write() > 0], [], 10)

			for x in iwtd:
				if x in self.clients:
					self.clients[x].readNotification() # if the socket exists, read incoming information
				else:
					(conn, addr) = x.accept() # if the socket does not exists, accept the new connection

					try:
						self.clients[conn] = Client(self, conn) # creates Client class obeject
						# if self.matchNickname(self.clients[conn].nickname):
						# 	conn.close()
						# 	continue
						self.printInformation("Connection Accepted from %s:%s" % (addr[0], addr[1]))
					except socket.error:
						try:
							conn.close() # if any error occurs, try to close the connection
						except:
							pass

			for x in owtd:
				if x in self.clients:
					self.clients[x].writeNotification() # sending information to the existing clients


################################################ SERVER CLASS END ##########################################################################



"""
Next 4 lines of code taken from the following source:

https://github.com/jrosdahl/miniircd/blob/master/miniircd
"""
_maketrans = str.maketrans
_ircstring_translation = _maketrans(string.ascii_lowercase.upper() + "[]\\^", string.ascii_lowercase + "{}|~")
def irc_lower(s):
	return s.translate(_ircstring_translation)






# main function to start the program
def main():
	server = Server() # create a Server class object
	try:
		server.start() # preparing server
	except KeyboardInterrupt:   # close the server with a message if keyboard interruption happen
		print(f"Server close")

if __name__ == "__main__":
	main()