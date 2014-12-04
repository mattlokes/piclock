import Queue
import time
import frameLib
import signal
import sys

import hwInterface
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

rxCmd = Queue.Queue()
txCmd = Queue.Queue()
frame = Queue.Queue()

hw = hwInterface.hwInterface ( frame, txCmd, rxCmd, True )
hw.startup()

ca = clockApp.clockApp( frame, txCmd, rxCmd )
ca.startup()

ws = wsInterface.wsInterface( rxCmd)
ws.startup()

while True:
   time.sleep(5)


