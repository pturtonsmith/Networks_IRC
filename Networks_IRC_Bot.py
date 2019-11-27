from datetime import datetime
import time
import socket
from random import seed
from random import random
from random import randint
import errno
import sys

Header_Length = 10
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def joinServer(server, channel):
    botuname = "IRC_Bot"
    print("Connecting to: " + server + " as " + botuname)
    irc.connect((server, 6667))

    irc.send(bytes("USER " + botuname + " " + botuname + " " + botuname + " :Channel Robot\n", "utf-8"))
    irc.send(bytes("NICK Bot\n", "utf-8"))
    time.sleep(5)
    irc.send(bytes("JOIN " + channel + "\n", "utf-8"))


def recievePacket():
    time.sleep(1)
    return irc.recv(2040).decode("utf-8")


def parseCommand(input):
    split = input.split(' ', 2)
    command = split[0]
    print("Command: " + split[0] + ", reciprient: " + split[1] + ", message: " + split[2])
    if (command == 'PONG'):
        pingServer(split[1], split[2])
    elif (command == 'PRIVMSG'): # If message recieved
        reciprient = split[1]
        if ('#' in reciprient):
            channelMsg(split[1], split[2])
        elif (reciprient == 'bot'):
            privMsg(split[1], split[2])

def channelMsg(channel, message):
    forBot = False
    reply = ""
    if (message == "!time"):
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        reply = "The time is " + time_string
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
        reply = "Today is " + day_string
        forBot = True
    if (forBot == True):
        print(reply)
        msgReply(channel, reply)

def privMsg(sender, msgRecv):
    reply = ""
    if ("hi bot" in msgRecv):
        reply = "Hi " + sender + "!"
    else:
        rand = randint(1, 3)
        switcher = {
            1: "some random fact no.1",
            2: "This bot isn't great",
            3: "something else",
            4: "what else is there",
            5: "42",
            6: "27"}
        reply = switcher.get(rand)
    msgReply(sender, reply)

def pingServer(part1, part2):
    reply = "PING ", part1, part2, "\r\n"
    #pingReply(servAddr, msgReply)

def msgReply(reciprient, msg):
    print(reciprient + "," + msg)
    print("Full Reply with:")
    fullMsg = "PRIVMSG " + reciprient + " " + msg
    print(fullMsg)
    encodeMsg = fullMsg.encode("utf-8")
    msgHeader = f"{len(encodeMsg):^{Header_Length}}".encode("utf-8")
    irc.send(msgHeader + encodeMsg)


server = sys.argv[1]
uname = "IRC_Bot"
print("Connecting to: " + server + " as " + uname)
# joinServer(server, sys.argv[2])
irc.connect((server, 6667))

botuname = uname.encode("utf-8")
unameHeader = f"{len(botuname):^{Header_Length}}".encode("utf-8")
irc.send(unameHeader + botuname)
time.sleep(5)

#irc.send(bytes("JOIN " + channel + "\n", "utf-8"))

try:
    while True:
        unameHeader = irc.recv(Header_Length)
        print(unameHeader)
        if not len(unameHeader):
            print("Server Disconnected")
            sys.exit()
        username_Length = int(unameHeader.decode('utf-8'))
        uname = irc.recv(username_Length).decode('utf-8')
        msg_Header = irc.recv(Header_Length)
        msg_Length = int(msg_Header.decode('utf-8'))
        msg = irc.recv(msg_Length).decode('utf-8')
        print(msg)
        parseCommand(msg)

# Error handling
except IOError as ex:
    if ex.errno != errno.EAGAIN and ex.errno != errno.EWOULDBLOCK:
        print('IO Error: {}'.format(str(ex)))
        sys.exit()
# Error handling
except Exception as ex:
    print('Error: {}'.format(str(ex)))
    sys.exit()
