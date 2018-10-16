#! /usr/bin/env python3
import sys, os, socket, params, time
from threading import Thread
from threading import Lock
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        fileODone = False
        while True:
            msg = self.fsock.receivemsg()
            if msg:
                fileString = msg.decode().replace("\x00", "\n")

                if not fileODone:
                    auxS = fileString.split("//myname")
                    if auxS[0] in myDict:
                        myLock = myDict(auxS[0])
                        myLock.acquire()
                    else:
                        myDict[auxS[0]] = Lock()

                    myPath = os.path.join(os.getcwd()+"/receiving/"+auxS[0])
                    myFile = open(myPath, "w+")
                    myFile.write(auxS[1])
                    fileODone = True
                
                myFile.write(fileString)
            else:
                myFile.close()
                break
            """
            if not msg:
                if self.debug: print(self.fsock, "server thread done")
                return
            """


            """
            requestNum = ServerThread.requestCount
            time.sleep(0.001)
            ServerThread.requestCount = requestNum + 1
            msg = ("%s! (%d)" % (msg, requestNum)).encode()
            self.fsock.sendmsg(msg)
            """
global myDict
myDict = dict()

while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)