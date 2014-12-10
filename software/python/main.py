import Queue
import time
import frameLib
import signal
import sys

#import hwInterface
import wsInterface

import clockApp

def sigIntHandler(signal, frame):
   global hw
   global ca
   print " SigInt"
   hw.kill()
   ca.kill()
   ws.kill()
   time.sleep(2)
   sys.exit(0)

signal.signal(signal.SIGINT, sigIntHandler)

rxPipe = Queue.Queue()
txPipe = Queue.Queue()
fakePipe = Queue.Queue()

hw = hwInterface.hwInterface ( txPipe, fakePipe, True )
hw.startup()

ca = clockApp.clockApp( txPipe, rxPipe )
ca.startup()

ws = wsInterface.wsInterface( rxPipe )
ws.startup()

while True:
   time.sleep(5)


