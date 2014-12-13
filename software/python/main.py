import Queue
import time
import signal
import sys

from framework.webserver.webServer import *

from interfaces.hwInterface import *
from interfaces.wsInterface import *

#from applications.clockApp.clockApp import *
from applications.colourTestApp.colourTestApp import *

def sigIntHandler(signal, frame):
   global hw
   global ca
   print " SigInt"
   wbs.kill()
   hw.kill()
   #ca.kill()
   cta.kill()
   ws.kill()
   time.sleep(2)
   sys.exit(0)

fakeSerial=False
fastRx=True

signal.signal(signal.SIGINT, sigIntHandler)

rxPipe = Queue.Queue()
txPipe = Queue.Queue()
fakePipe = Queue.Queue()

if len(sys.argv) > 1:
   if "-fakeSerial" in sys.argv: fakeSerial=True
   if "-fastRx"     in sys.argv: fastRx=True
   if "-debugRx"    in sys.argv: fastRx=False

wbs = webServer()
wbs.start()

hw = hwInterface ( fakePipe, txPipe, fastRx, fakeSerial )
hw.startup()

cta = colourTestApp(txPipe, rxPipe)
cta.startup()

#ca = clockApp( txPipe, rxPipe )
#ca.startup()

ws = wsInterface( rxPipe )
ws.startup()

while True :
   time.sleep(5)


