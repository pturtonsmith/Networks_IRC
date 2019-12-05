from datetime import datetime
import time
import socket
from random import seed
from random import random
from random import randint
import errno
import sys


# Connection details
serverIP = "10.0.42.17"
port = 6667
channel = "#test"

# Setup socket
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def joinServer(): # Join server
    print("Connecting to: " + serverIP + " as " + uname)
    irc.connect((serverIP, port))
    # Attempt to connect to IRC server, send username & nickname
    irc.send(bytes("NICK " + uname + "\r\n", "utf-8"))
    irc.send(bytes("USER " + uname + " " + uname + " * :PRObot\r\n", "utf-8"))
    reply = irc.recv(1024).decode("utf-8")
    individMsg = reply.split('\r\n')
    initErrNotFound = True
    nickErrNotFound = True
    for msg in individMsg:
        if (len(msg) > 0):
            splitMsg = msg.split(' ')
            if(splitMsg[1] != "001") and initErrNotFound: # If error message returned & sucess not already returned
                print(reply)
                print("Was not able to establish connection to server")
                sys.exit(1)
            else:
                initErrNotFound = False
            if(splitMsg[1] == "433") and nickErrNotFound: # If nickname already taken, another bot is running
                print("Nickname already in use, please disconnect other user/bot and try again")
                sys.exit(1)
            else:
                nickErrNotFound = False
    print("Connection to " + serverIP + " established!")
    time.sleep(2)
    irc.send(bytes("JOIN " + channel + "\n", "utf-8")) # Join channel 
    reply = irc.recv(2048).decode("utf-8")
    

def parseCommand(input): # Determine type of message - ping, channel message or direct message (PM)
    print(input)
    if ('PING' in input): # If ping recieved, send pong back
        servName = input.split(' ')[1][1:]
        pingServer(servName)
    elif ('PRIVMSG' in input): # If message recieved, determine channel or direct message
        split = input.split(' ', 3)
        sender = input.split('!',1)[0][1:]
        message = input.split('PRIVMSG',1)[1].split(':',1)[1]
        message = message.strip('\n')
        reciprient = split[2]
        if ('#' in reciprient): # If channel
            channelMsg(reciprient, message)
        elif (uname in reciprient): # Or if private message to bot
            privMsg(sender, message)


def channelMsg(recChannel, message): # Messages sent in channel
    forBot = False
    reply = ""
    if ("!time" in message): # If message looking for time, then message is for bot
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        reply = "The time is " + time_string
        forBot = True
    elif ("!day" in message): # If message looking for day, then message is for bot
        now = datetime.now() # Get date & day of week
        day_int = now.isoweekday()
        day = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday"
        }
        reply = "Today is " + day.get(day_int) + " " + now.strftime("%d %B %Y")
        forBot = True 
    if (forBot == True): # If message was for bot, then send reply
        print(reply)
        msgReply(recChannel, reply)


def privMsg(sender, msgRecv): # Messages sent directly to bot (PM)
    reply = ""
    if ("hi bot" in msgRecv):
        reply = "Hi " + sender + "!"
    elif ("!time" in msgRecv): # If user looking for time, then message is for bot
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        reply = "The time is " + time_string
    elif ("!day" in msgRecv): # If user looking for day of week, then message is for bot
        now = datetime.now() # Get date & day of week
        day_int = now.isoweekday()
        day = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday"
        }
        reply = "Today is " + day.get(day_int) + " " + now.strftime("%d %B %Y")
    else: # Randomly choose a fact or nonsense sentence to reply with
        rand = randint(1, 10)
        switcher = {
            1: "The backbone of the internet is made up of 550,000 miles of underwater cable.",
            2: "This bot is alright",
            3: "The Internet consists of five billion computing devices such as computers, phones, modems, switches, routers etc.",
            4: "An email takes around 2 billion electrons to produce.",
            5: "Everyday a grape licks a friendly cow.",
            6: "27",
            7: "Internet is controlled by 75 million servers.",
            8: "I am so blue I'm greener than purple.",
            9: "Random nonsense",
            10: "If your canoe is stuck in a tree with the headlights on, how many pancakes does it take to get to the moon?"}
        reply = switcher.get(rand)
    msgReply(sender, reply)


def pingServer(serverAddr): # Send a 'pong' back to the server
    msgReply = "PONG " + serverAddr + "\r\n"
    irc.send(msgReply.encode("utf-8"))


def msgReply(reciprient, msg): # Formats and sends a message in response
    fullMsg = "PRIVMSG " + reciprient + " :" + msg + "\r\n"
    print(fullMsg)
    encodeMsg = fullMsg.encode("utf-8")
    irc.send(encodeMsg)
    

def disconnect(): # Disconnect from server gracefully
    fullMsg = "QUIT " + uname
    print(fullMsg)
    irc.send(fullMsg.encode("utf-8"))
    reply = irc.recv(1024).decode("utf-8")
    while fullMsg not in reply:
        reply = irc.recv(1024).decode("utf-8")


uname = "IRC_Bot"
joinServer()

try: # While program is running, try to recieve messages
    while True:
        msg = irc.recv(1024).decode("utf-8")
        if not len(msg): # If no message recieved, quit
            print("Server Disconnected")
            sys.exit()
        parseCommand(msg) # Determine type of message & reply

# Error handling
except KeyboardInterrupt: # If interrupted by user entering Ctrl-C then ensure a clean exit from server first
    print("Disconnecting from server...")
    disconnect()
    sys.exit(1)
except IOError as ex:
    if ex.errno != errno.EAGAIN and ex.errno != errno.EWOULDBLOCK:
        print('IO Error: {}'.format(str(ex)))
        sys.exit(1)
# Error handling
except Exception as ex:
    print('Error: {}'.format(str(ex)))
    sys.exit(1)

