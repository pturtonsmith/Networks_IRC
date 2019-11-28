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
    print("USER " + botuname + " " + botuname + " * :Channel Robot\r\n")
    # Attempt to connect to IRC server, send username & nickname
    irc.send(bytes("USER " + botuname + " " + botuname + " * :Channel Robot\r\n", "utf-8"))
    irc.send(bytes("NICK Channel_Bot\r\n", "utf-8"))
    reply = irc.recv(1024).decode("utf-8")
    # print(reply)
    individMsg = reply.split('\r\n')
    initErrNotFound = True
    nickErrNotFound = True
    for msg in individMsg:
        if (len(msg) > 0):
            print(msg)
            splitMsg = msg.split(' ')
            if(splitMsg[1] != "001") and initErrNotFound: # If error message returned & sucess not already returned
                print(reply)
                print("Was not able to establish connection to server")
                sys.exit(1)
            else:
                initErrNotFound = False
            if(splitMsg[1] == "433") and nickErrNotFound: # If nickname already taken, another bot is running
                print("Nickname already in use, please disconnect other bot and try again")
                sys.exit(1)
            else:
                nickErrNotFound = False
    
    time.sleep(2)
    irc.send(bytes("JOIN " + channel + "\n", "utf-8")) # Join channel user entered in arguments
    reply = irc.recv(2048).decode("utf-8")
    print(reply)


def recievePacket():
    time.sleep(1)
    return irc.recv(2040).decode("utf-8")


def parseCommand(input): # Determine type of message
    # split = input.split(' ', 4)
    # command = split[1]
    #print("Command: " + split[0] + ", reciprient: " + split[1] + ", message: " + split[2])
    if ('PING' in input):
        servName = input.split(' ')[1][1:]
        print(servName)
        pingServer(servName)
    elif ('PRIVMSG' in input): # If message recieved
        split = input.split(' ', 3)
        for ind in split:
            print(ind)
        sender = input.split('!',1)[0][1:]
        message = input.split('PRIVMSG',1)[1].split(':',1)[1]
        message = message.strip('\n')
        reciprient = split[2]
        print("Sender: " + sender)
        print("Message: " + message)
        print("Reciprient: " + reciprient)
        if ('#' in reciprient):
            channelMsg(reciprient, message)
        elif ("Bot" in reciprient):
            privMsg(sender, message)


def channelMsg(channel, message): # Messages sent in channel
    forBot = False
    reply = ""
    print(f"channel: {channel}, message: {message}")
    if ("!time" in message): # If user looking for time, then message is for bot
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        reply = "The time is " + time_string
        forBot = True
    elif ("!day" in message): # If user looking for day of week, then message is for bot
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
    if (forBot == True): # If message was for bot, then send reply
        print(reply)
        msgReply(channel, reply)


def privMsg(sender, msgRecv): # Messages sent directly to bot (PM)
    reply = ""
    if ("hi bot" in msgRecv):
        reply = "Hi " + sender + "!"
    else: # Randomly choose a fact or nonsense sentence to reply with
        rand = randint(1, 10)
        switcher = {
            1: "The backbone of internet is made up of 550,000 miles of underwater cable.",
            2: "This bot isn't great",
            3: "Internet consists of five billion computing devices such as computers, phones, modems, switches, routers etc.",
            4: "An email takes around 2 billion electrons to produce.",
            5: "Everyday a grape licks a friendly cow.",
            6: "27",
            7: "Internet is controlled by 75 million servers.",
            8: "I am so blue I'm greener than purple.",
            9: "Random nonsense",
            10: "If your canoe is stuck in a tree with the headlights on, how many pancakes does it take to get to the moon?"}
        reply = switcher.get(rand)
    msgReply(sender, reply)

def pingServer(serverAddr):
    msgReply = "PONG " + serverAddr + "\r\n"
    irc.send(msgReply.encode("utf-8"))

def msgReply(reciprient, msg): # Formats and sends a message in response
    # print(reciprient + "," + msg)
    # print("Full Reply with:")
    fullMsg = "PRIVMSG " + reciprient + " :" + msg + "\r\n"
    # print(fullMsg)
    encodeMsg = fullMsg.encode("utf-8")
    irc.send(encodeMsg)
    # msgHeader = f"{len(encodeMsg):^{Header_Length}}".encode("utf-8")
    # irc.send(msgHeader + encodeMsg)


server = sys.argv[1]
uname = "IRC_Bot"
print("Connecting to: " + server + " as " + uname)
joinServer(server, sys.argv[2])
# irc.connect((server, 6667))

# botuname = uname.encode("utf-8")
# unameHeader = f"{len(botuname):^{Header_Length}}".encode("utf-8")
# irc.send(unameHeader + botuname)
# time.sleep(3)

#irc.send(bytes("JOIN " + channel + "\n", "utf-8"))

try: # While program is running, try to recieve messages
    while True:
        msg = irc.recv(1024).decode("utf-8")
        print(msg)
        if not len(msg): # If no message recieved, quit
            print("Server Disconnected")
            sys.exit()
        # print("unameheader: " + msg.decode("utf-8"))
        
        # username_Length = int(unameHeader.decode("utf-8"))
        # uname = irc.recv(username_Length).decode("utf-8") # Recieve rest of message
        # msg_Header = irc.recv(Header_Length)
        # msg_Length = int(msg_Header.decode("utf-8"))
        # msg = irc.recv(msg_Length).decode("utf-8")
        # print(msg)
        parseCommand(msg) # Determine type of message & reply

# Error handling
except IOError as ex:
    if ex.errno != errno.EAGAIN and ex.errno != errno.EWOULDBLOCK:
        print('IO Error: {}'.format(str(ex)))
        sys.exit()
# Error handling
except Exception as ex:
    print('Error: {}'.format(str(ex)))
    sys.exit()
