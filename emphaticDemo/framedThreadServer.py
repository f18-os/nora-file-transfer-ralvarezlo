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
        print("Thread Running")
        fileODone = False
        fName = ""
        while True:
            print("initialized loop")
            msg = self.fsock.receivemsg()
            if msg:
                print("message received")
                fileString = msg.decode().replace("\x00", "\n")

                if not fileODone:
                    auxS = fileString.split("//myname")
                    fName = auxS[0]
                    if fName in myDict:
                        print("It's in Dictionary: " + fName)
                        myLock = myDict[fName]
                        myLock.acquire()
                    else:
                        print("It's not in Dictionary: " + fName)
                        myDict[fName] = Lock()
                        myDict[fName].acquire()
                        print("lock done")

                    myPath = os.path.join(os.getcwd()+"/receiving/"+auxS[0])
                    myFile = open(myPath, "w+")
                    myFile.write(auxS[1])
                    fileODone = True
                    print("File Opened: " + fName)
                else: 
                    print("In Msg, fileODone true")
                    myFile.write(fileString)
                msg = msg + b"!"
                requestNum = ServerThread.requestCount
                time.sleep(0.001)
                ServerThread.requestCount = requestNum + 1
                msg = ("%s! (%d)" % (msg, requestNum)).encode()
                self.fsock.sendmsg(msg)

            if not msg:
                print("File Ending")
                myDict[fName].release() #Release Lock
                myDict.pop(fName) #Remove Key
                myFile.close()
                return
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
    print("Socket Accepted, calling thread")
    ServerThread(sock, debug)