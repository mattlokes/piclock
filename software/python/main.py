import Queue
import time
import signal
import sys

from framework.webserver.webServer import *

from interfaces.hwInterface import *
from interfaces.wsInterface import *

from applications.clockApp.clockApp import *
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

modules = {
           'DISP': 
           {'class':"hwInterface", 'state': "running", 'obj': None,
            'txPipe': None, 'rxPipe': None, 'args': [fastRx, fakeSerial] },
           'WEBSOCK':
           {'class':"wsInterface", 'state': "running", 'obj': None,
            'txPipe': None },
           'WEBSERVER': 
           {'class':"webServer", 'state': "running", 'obj': None},
           'CLOCK':
           {'class':"clockApp", 'state': "running", 'obj': None,
            'txPipe': None, 'rxPipe': None },
           'COLTEST': 
           {'class':"colourTestApp", 'state': None, 'obj': None,
            'txPipe': None, 'rxPipe': None }
          }

#Go through Modules Instantiating them all and starting up
for name, module in modules.iteritems():
   argList = []
   if module['state'] is "running":
      if 'txPipe' in module.keys():
         module['txPipe'] = Queue.Queue()
         argList.append(module['txPipe'])
      if 'rxPipe' in module.keys():
         module['rxPipe'] = Queue.Queue()
         argList.append(module['rxPipe'])
      if 'args' in module.keys():
         argList += module['args']
      module['obj'] = eval(module['class'])(*argList)
      module['obj'].startup()

#MAIN LOOP Check for Messages from all modules and route them
while True:
   for name, module in modules.iteritems():
      try:
         msg = module['txPipe'].get(timeout=0.01)
      except:
         pass
      else:
         modules[msg['dst']]['rxPipe'].put(msg)

###########################################
#wbs = webServer()
#wbs.start()

#hw = hwInterface ( fakePipe, txPipe, fastRx, fakeSerial )
#hw.startup()

#cta = colourTestApp(txPipe, rxPipe)
#cta.startup()

#ca = clockApp( txPipe, rxPipe )
#ca.startup()

#ws = wsInterface( rxPipe )
#ws.startup()

while True :
   time.sleep(5)


