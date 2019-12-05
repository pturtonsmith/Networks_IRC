import os
import select
import socket
import string
import sys
import time


def buffer_to_socket(msg):
	return msg.encode()

def socket_to_buffer(buf):
	return buf.decode(errors="ignore")

class Channel(object):
	def __init__(self, server, name):
		print("Creating channel with name " + name)
		self.server = server
		self.name = name
		self.members = set()

	def add_member(self, client):
		print(sys._getframe().f_code.co_name)
		self.members.add(client)

	def remove_client(self, client):
		print(sys._getframe().f_code.co_name)
		self.members.discard(client)
		if not self.members:
			client.server.remove_channel(self)
	


class Client(object):
	def __init__(self, server, socket):
		print(__name__ + " client")
		self.server = server
		self.socket = socket
		self.channels = {}
		self.nickname = None
		self.user = None
		self.realname = None

		self.host, self.port = socket.getpeername()

		self.readbuffer = ""
		self.writebuffer = ""
		
	def get_prefix(self):
		print(sys._getframe().f_code.co_name)
		return "%s!%s@%s" % (self.nickname, self.user, self.host)
	prefix = property(get_prefix)

	def wite_queue_size(self):
		return len(self.writebuffer)

	def __parse_read_buffer(self):
		print(sys._getframe().f_code.co_name)
		lines = self.readbuffer
		self.readbuffer = lines[-1]
		lines = lines[:-1]
		print(lines)
		for line in lines.split('\r\n'):
			print(line)
			if not line:
				continue
			x = line.split(" ", 1)
			command = x[0]
			
			if len(x) == 1:
				arguments = []
			else:
				if len(x[1]) > 0 and x[1][0] == ":":
					arguments = [x[1][1:]]
				else:
					y = x[1].split(" :", 1)
					arguments = y[0].split()
					if len(y) == 2:
						arguments.append(y[1])
				print(command)
				print(arguments)
				self.__command_handler(command, arguments)
				

	def message(self, msg):
		print(sys._getframe().f_code.co_name)
		print("client: ", self.user, " @ ", self.host)
		self.writebuffer += msg + "\r\n"

	def __command_handler(self, command, arguments):
		def user_handler():
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


		def nick_handler():
			print("Nick handler")
			if len(arguments) < 1:
				self.message("Not enough parameters")
			print(arguments)
			self.nickname = arguments[0]
			print("Nickname set to " + self.nickname)

		def join_handler():
			print("Join_Handler")
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

		def privmsg_handler():
			targetname = arguments[0]
			message = arguments[1]
			print("Targetname = " + targetname)
			client = server.find_client(targetname)
			print("Client returned = %s", client)
			if server.has_channel(targetname):
				print("Send to channel")
				channel = server.get_channel(targetname)
				self.message_channel(channel, command, "%s :%s" % (channel.name, message))
			elif client:
				print("PM to user")
				prefix = self.prefix
				print("Prefix: ", prefix, " command: ", command, " target: ", targetname, " message: ", message)
				messageToSend = ":%s %s %s :%s" % (prefix, command, targetname, message)
				print(messageToSend)
				client.message(messageToSend)

		def part_handler():
			if len(arguments) > 1:
				partmsg = arguments[1]
			else:
				partmsg = self.nickname
			for channelname in arguments[0].split(","):
				if channelname:
					if channelname in self.channels:
						channel = self.channels[irc_lower(channelname)]
						self.message_channel(channel, "PART", "%s :%s" % (channelname, partmsg), True)
						del self.channels[irc_lower(channelname)]
						server.remove_member_from_channel(self, channelname)

		def quit_handler():
			if len(arguments) < 1:
				quitmsg = self.nickname
			else:
				quitmsg = arguments[0]
			self.disconnect(quitmsg)

		handler_table = {"USER": user_handler, "NICK": nick_handler, "JOIN": join_handler, "PRIVMSG": privmsg_handler, "PART": part_handler, "QUIT": quit_handler}
		server = self.server
		try:
			print("start of command handler")
			if '\n' in command:
				command = command.split('\n')[1]
			print("command = " + command)
			handler = handler_table.get(command)
			if handler:
				handler()
		except KeyError:
			self.message("Unknown Command")

	def disconnect(self, quitmsg):
		print(sys._getframe().f_code.co_name)
		self.message("Error: %s" % quitmsg)
		self.server.print_info("Disconnected connection from %s" % self.host)
		self.socket.close()
		self.server.remove_client(self, quitmsg)

	def message_channel(self, channel, command, message, include_self=False):
		print("message channel")
		line = ":%s %s %s" % (self.prefix, command, message)
		print(line)
		for client in channel.members:
			if client != self or include_self:
				client.message(line)


	def socket_readable_notification(self):
		print(sys._getframe().f_code.co_name)
		try:
			data = self.socket.recv(2048)
			quitmsg = "EOT"
		except socket.error as x:
			data = ""
			quitmsg = x

		if data:
			self.readbuffer += socket_to_buffer(data)
			self.__parse_read_buffer()
		else:
			self.disconnect(quitmsg)


	def socket_writable_notification(self):
		print(sys._getframe().f_code.co_name)
		try:
			sent = self.socket.send(buffer_to_socket(self.writebuffer))
			self.writebuffer = self.writebuffer[sent:]
		except socket.error as x:
			self.disconnect(x)


	def joinChannel(self, channelToJoin):
		print("in join channel")
		channelToJoin.add_member(self)
		self.channels[channelToJoin.name] = channelToJoin
		self.message_channel(channelToJoin, "JOIN", channelToJoin.name, True)
		whoinMsg = ":" + self.server.name + " 353 " + self.nickname + " = " + channelToJoin.name
		for member in channelToJoin.members:
			whoinMsg += " " + member.nickname
		self.message(whoinMsg)
		endNameMsg = ":" + self.server.name + " 366 " + self.nickname + " " + channelToJoin.name + " :End of NAMES list"
		self.message(endNameMsg)



class Server(object):
	def __init__(self):
		self.address = ""
		self.name = socket.getfqdn(self.address)[:63]
		self.channels = {}
		self.clients = {}
		self.nicknames = {}

	def find_client(self, nickname):
		for client in self.clients.values():
			if client.nickname == nickname:
				return client

	def has_channel(self, name):
		return irc_lower(name) in self.channels

	def get_channel(self, channelname):
		if irc_lower(channelname) in self.channels:
			channel = self.channels[irc_lower(channelname)]
		else:
			channel = Channel(self, channelname)
			self.channels[irc_lower(channelname)] = channel
		return channel

	def remove_member_from_channel(self, client, channelname):
		if irc_lower(channelname) in self.channels:
			channel = self.channels[irc_lower(channelname)]
			channel.remove_client(client)

	def remove_client(self, client, quitmsg):
		client.message_related(":%s QUIT :%s" % (client.prefix, quitmsg))
		for x in client.channels.values():
			x.remove_client(client)
		del self.clients[client.socket]

	def remove_channel(self, channel):
		del self.channels[irc_lower(channel.name)]

	def print_info(self, msg):
		print(msg)
		sys.stdout.flush()

	def start(self):
		serversockets = []
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		port = 6667

		try:
			s.bind((self.address, port))
		except:
			print ("Cannot bind")
			sys.exit(1)

		s.listen()
		serversockets.append(s)
		del s
		print(f"Listening for connections on :{port}")
		self.run(serversockets)


	def run(self, serversockets):
		while True:
			(iwtd, owtd, ewtd) = select.select(serversockets + [x.socket for x in self.clients.values()], [x.socket for x in self.clients.values() if x.wite_queue_size() > 0], [], 10)

			for x in iwtd:
				if x in self.clients:
					self.clients[x].socket_readable_notification()
				else:
					(conn, addr) = x.accept()

					try:
						self.clients[conn] = Client(self, conn)
						self.print_info("Connection Accepted from %s:%s" % (addr[0], addr[1]))
					except socket.error:
						try:
							conn.close()
						except:
							pass

			for x in owtd:
				if x in self.clients:
					self.clients[x].socket_writable_notification()

# Link for upper-lowercase string convert
_maketrans = str.maketrans
_ircstring_translation = _maketrans(string.ascii_lowercase.upper() + "[]\\^", string.ascii_lowercase + "{}|~")
def irc_lower(s):
	return s.translate(_ircstring_translation)

def main():
	server = Server()
	try:
		server.start()
	except KeyboardInterrupt:
		print(f"Server close")

if __name__ == "__main__":
	main()
