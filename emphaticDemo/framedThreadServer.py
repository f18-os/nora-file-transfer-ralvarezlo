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
        fName = ""
        while True:
            msg = self.fsock.receivemsg()
            if msg:
                fileString = msg.decode().replace("\x00", "\n")

                if not fileODone: #To Create a New File if it's the first line received
                    auxS = fileString.split("//myname")
                    fName = auxS[0]
                    if fName in myDict: #If file exist we should acquire the corresponding lock in the dictionary to wait for the colliding thread to end
                        print("It's in Lock Dictionary: " + fName)
                        myLock = myDict[fName]
                        myLock.acquire()
                    else: #If it doesn't we create the lock and acquire it
                        print("It's not in Lock Dictionary: " + fName)
                        myDict[fName] = Lock()
                        myDict[fName].acquire()
                        print("lock done")

                    myPath = os.path.join(os.getcwd()+"/receiving/"+auxS[0])
                    myFile = open(myPath, "w+")
                    myFile.write(auxS[1])
                    fileODone = True
                    print("File Opened: " + fName)
                else: #If it's another line we just append it
                    print("In Msg, fileODone true")
                    myFile.write(fileString)
                msg = msg + b"!"
                requestNum = ServerThread.requestCount
                time.sleep(0.001)
                ServerThread.requestCount = requestNum + 1
                msg = ("%s! (%d)" % (msg, requestNum)).encode()
                self.fsock.sendmsg(msg)

            if not msg: #When we have stopped receiving messages
                print("File Ending: "+fName)
                myDict[fName].release() #Release Lock
                myDict.pop(fName) #Remove Key
                myFile.close()
                return

global myDict
myDict = dict()

while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)