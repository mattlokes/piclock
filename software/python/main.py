import Queue
import time
import signal
from sys import *

from libraries.systemLib import *

from framework.webserver.webServer import *

from interfaces.hwInterface import *
from interfaces.wsInterface import *

from applications.clockApp.clockApp import *
from applications.colourTestApp.colourTestApp import *

def sigIntHandler(signal, frame):
   print ""
   killModules()
   #time.sleep(2)
   exit(0)

def killModules():
   for name, module in modules.iteritems():
      if module['state'] is "R":
         if name is not "WEBSOCK" and "rxPipe" in module.keys(): #If Module is running and rxPipe send KILL Msg
            module['rxPipe'].put({'dst':name, 'src':"MAIN", 'typ':"KILL", 'dat':0})
         else:                         #Else Use Kill Function
            module['obj'].kill()

fakeSerial=False
fastRx=True
noDisp=False
debugSys=False

signal.signal(signal.SIGINT, sigIntHandler)

if len(sys.argv) > 1:
   if "-termDisp" in sys.argv: fakeSerial=True
   if "-noDisp"   in sys.argv: noDisp=True
   if "-debugRx"  in sys.argv: fastRx=False
   if "-debugSys" in sys.argv: debugSys=True

sys = sysPrint("MAIN", debugSys)

# Module State: R=Running, I=Initialized & P=Paused
modules = {
           'DISP': 
           {'class':"hwInterface", 'state': "R", 'obj': None,
            'txPipe': None, 'rxPipe': None, 'args': [fastRx, fakeSerial,debugSys] },
           'WEBSOCK':
           {'class':"wsInterface", 'state': "R", 'obj': None,
            'txPipe': None, 'rxPipe': None, 'args': [debugSys] },
           'WEBSERVER': 
           {'class':"webServer", 'state': "R", 'obj': None },
           'CLOCK':
           {'class':"clockApp", 'state': "R", 'obj': None,
            'txPipe': None, 'rxPipe': None, 'args': [debugSys] },
           'COLTEST': 
           {'class':"colourTestApp", 'state': None, 'obj': None,
            'txPipe': None, 'rxPipe': None, 'args': [debugSys] }
          }

if noDisp: modules['DISP']['state'] = None

#Go through Modules Instantiating them all and starting up
for name, module in modules.iteritems():
   argList = []
   if module['state'] is "R":
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
         try:
            modules[msg['dst']]['rxPipe'].put(msg)
         except:
            sys.error("Cmd Destination {0} does not exist".format(msg['dst']))
   time.sleep(0.01)
