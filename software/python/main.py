import Queue
import time
import signal
from sys import *

from libraries.systemLib import *
from framework.components.application import *

from framework.webserver.webServer import *

from interfaces.hwInterface import *
from interfaces.wsInterface import *

from applications.clockApp.clockApp import *
from applications.colourTestApp.colourTestApp import *

def sigIntHandler(signal, frame):
   print ""
   killModules()
   exit(0)

def killModules():
   for name, module in modules.iteritems():
      if module['enabled']:
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

modules = {
           'DISP': 
           {'class': hwInterface, 'type': "INTER", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'fastRx': fastRx, 'fakeSerial': fakeSerial, 'debugSys': debugSys} },
           'WEBSOCK':
           {'class': wsInterface, 'type': "INTER", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys': debugSys} },
           'WEBSERVER': 
           {'class': webServer, 'type': "INTER", 'obj': None, 'enabled': True},
           'CLOCK':
           {'class': clockApp, 'type': "APP", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys':debugSys} },
           'COLOUR': 
           {'class': colourTestApp , 'type': "APP", 'obj': None, 'enabled': False,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys':debugSys} }
          }

if noDisp: modules['DISP']['state'] = None

#Go through Modules Instantiating them all and starting up
for name, module in modules.iteritems():
   argList = []
   if module['enabled']:
      
      if   module['type'] is "INTER":
         modClass = module['class']
      elif module['type'] is "APP":
         modClass = application
         argList.append(module['class'])
      else:
         pass

      if 'txPipe' in module.keys():
         module['txPipe'] = Queue.Queue()
         argList.append(module['txPipe'])
      if 'rxPipe' in module.keys():
         module['rxPipe'] = Queue.Queue()
         argList.append(module['rxPipe'])
      if 'args' in module.keys():
         argList += module['args']

      if 'kwargs' in module.keys():
         module['obj'] = modClass(*argList,**module['kwargs'])
      else:
         module['obj'] = modClass(*argList)

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
