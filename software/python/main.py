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
   print " SigInt"
   time.sleep(2)
   sys.exit(0)

fakeSerial=False
fastRx=True

signal.signal(signal.SIGINT, sigIntHandler)


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
         msg = module['txPipe'].get(block=False)
      except:
         pass
      else:
         modules[msg['dst']]['rxPipe'].put(msg)
   time.sleep(0.01)

while True :
   time.sleep(5)


