#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
import params
from framedSock import FramedStreamSock
from threading import Thread
from threading import Lock
import time

myHost = "50001"
while (1):
    userAns = input("Use proxy(\"p\") or local host 50001(\"l\")?")
    if(userAns=="p"):
        myHost = "50000"
        break
    elif(userAns=="l"):
        myHost = "50001"
        break
    else: print("Invalid selection, try again")

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:"+myHost),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
        s = None
        for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
           af, socktype, proto, canonname, sa = res
           try:
               print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
               s = socket.socket(af, socktype, proto)
           except socket.error as msg:
               print(" error: %s" % msg)
               s = None
               continue
           try:
               print(" attempting to connect to %s" % repr(sa))
               s.connect(sa)
           except socket.error as msg:
               print(" error: %s" % msg)
               s.close()
               s = None
               continue
           break

        if s is None:
           print('could not open socket')
           sys.exit(1)

        fs = FramedStreamSock(s, debug=debug)
        
        
        while (1): 
            try:
                fname = input("Please input name or 'exit' to end process:\n")
                if(fname=="exit"): os._exit(1)
                myFile = open(fname,'r')
                mlock.release()
                break
            except IOError:
                print("File doesn't exist, try again.")

        auxStr = myFile.read().replace("\n", "\0") #replace new lines to null characters
        myFile.close()
        auxStr = fname + "//myname" + auxStr  + '\n' #Added the //myname to distinguish between file name and body
        fs.sendmsg(auxStr.encode())
        fs.receivemsg() #Just to make sure the message is sent

#Locks are used to make sure to ask the user for the file, when it's selected the lock will be released and it will transfer in the background
mlock = Lock()
for i in range(100):
    mlock.acquire()
    ClientThread(serverHost, serverPort, debug)

