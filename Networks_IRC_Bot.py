from datetime import datetime
import time
import socket
from random import seed
from random import random
import sys






def joinServer(server, channel, irc):
    botuname = "IRC_Bot"
    print("Connecting to: " + server + " as " + botuname)
    irc.connect((server, 6667))
    
    irc.send(bytes("USER " + botuname + botuname + botuname + ":Channel Robot\n", "utf-8"))
    irc.send(bytes("NICK Bot\n", "utf-8"))
    time.sleep(5)

    irc.send(bytes("JOIN " + channel + "\n", "utf-8"))


def recievePacket():
    time.sleep(1)
    return irc.recv(2040).decode("utf-8")
    

def parseCommand(input):
	split = input.split(' ', 3)
	command = split[0]
	if (command == 'JOIN'):
		joinServer()
	elif (command == 'PONG'):
		pingServer(split[1], split[2])
	elif (command == 'PRIVMSG'): # If message recieved
		reciprient = split[1]
		if ('#' in reciprient) :
			channelMsg(split[1], split[2])
		elif (reciprient == 'bot'):
			privMsg(split[1], split[2])

def channelMsg(channel, message):
	forBot = False;
	reply = ''
	if (message == '!time'):
		now = datetime.now()
		time_string = now.strftime("%H:%M:%S")
		reply == "The time is ", time_string
		forBot = True
	elif (message =='!day'):
		now = datetime.now()
		day_int = now.isoweekday()
		day_string = ''
		if (day_int == 1):
			day_string = 'Monday'
		elif (day_int == 2):
			day_string = 'Tuesday'
		elif (day_int == 3):
			day_string = 'Wednesday'
		elif (day_int == 4):
			day_string = 'Thursday'
		elif (day_int == 5):
			day_string = 'Friday'
		elif (day_int == 6):
			day_string = 'Saturday'
		elif (day_int == 7):
			day_string = 'Sunday'
		reply == "Today is ", day_string
		forBot = True
	if (forbot == True):
		reply(channel, reply)

def privMsg(sender, msgRecv):
    msgReply = ''
    if ('hi bot' in msgRecv):
        msgReply = 'Hi ', sender, '!'
    else:
        seed(10)
        rand = randint(1, 3)
        switcher = {
            1: "some random fact no.1",
            2: "This bot isn't great",
            3: "something else"}
        msgReply = switcher.get(rand)
    reply(sender, msgReply)

def pingServer(part1, part2):
    msgReply = "PING ", part1, part2, "\r\n"
    reply(servAddr, msgReply)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
joinServer(sys.argv[1], sys.argv[2], irc)

while True:
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(16)
        if new_msg:
            msglen = int(msg)
            new_msg = False
        full_msg += msg.decode("utf-8")
        if len(full_msg)-HEADERSIZE == msglen:
            print(full_msg)
            parseCommand(full_msg)
            new_msg = True
            full_msg = ""