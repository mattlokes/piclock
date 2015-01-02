import Queue
import time
import signal
import threading

from sys import *

from libraries.systemLib import *
from framework.components.application import *

from framework.webserver.webServer import *

from interfaces.hwInterface import *
from interfaces.wsInterface import *

from applications.clockApp.clockApp import *
from applications.snakeApp.snakeApp import *
from applications.colourTestApp.colourTestApp import *

def sigIntHandler(signal, frame):
   killModules()
   exit(0)

def killModules():
   for name, module in modules.iteritems():
      if module['enabled']: module['obj'].kill()

def rxIncoming( cmd ):
   global runningApp
   if cmd['typ'] == "SWITCH":
      appToSwitch = cmd['dat']
      if appToSwitch in modules.keys() and appToSwitch is not runningApp:
         if modules[appToSwitch]['enabled']:
            modules[runningApp]['obj'].pause()
            modules[appToSwitch]['obj'].resume()
            runningApp = appToSwitch
      

fakeSerial=False
fastRx=True
noDisp=False
debugSys=False

defaultApp = "CLOCK"

signal.signal(signal.SIGINT, sigIntHandler)

if len(sys.argv) > 1:
   if "-termDisp" in sys.argv: fakeSerial=True
   if "-noDisp"   in sys.argv: noDisp=True
   if "-debugRx"  in sys.argv: fastRx=False
   if "-debugSys" in sys.argv: debugSys=True

sys = sysPrint("MAIN", debugSys)

modules = {
           'DISP': 
           {'class': hwInterface, 'type': "IFACE", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'fastRx': fastRx, 'fakeSerial': fakeSerial, 'debugSys': debugSys} },
           'WEBSOCK':
           {'class': wsInterface, 'type': "IFACE", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys': debugSys} },
           'WEBSERVER': 
           {'class': webServer, 'type': "IFACE", 'obj': None, 'enabled': True},
           'CLOCK':
           {'class': clockApp, 'type': "APP", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys':debugSys} },
           'SNAKE':
           {'class': snakeApp, 'type': "APP", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys':debugSys} },
           'COLOUR': 
           {'class': colourTestApp , 'type': "APP", 'obj': None, 'enabled': True,
            'txPipe': None, 'rxPipe': None, 'kwargs': {'debugSys':debugSys} }
          }

if noDisp: modules['DISP']['enabled'] = False

#Go through Modules Instantiating them all and starting up
for name, module in modules.iteritems():
   argList = []
   if module['enabled']:
      
      if   module['type'] is "IFACE":
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

      if 'kwargs' in module.keys():
         module['obj'] = modClass(*argList,**module['kwargs'])
      else:
         module['obj'] = modClass(*argList)

      module['obj'].startup()

#Start Default App
modules[defaultApp]['obj'].resume()
runningApp = defaultApp

#MAIN LOOP Check for Messages from all modules and route them
while True:
   for name, module in modules.iteritems():
      try:    cmd = module['txPipe'].get(block=False)
      except: pass
      else:
         if cmd['dst'] == "MAIN": #Packets sent to MAIN are pulled here
            rxIncoming( cmd )
         else:                    #Packets to be route here to other modules
            try:
               modules[cmd['dst']]['rxPipe'].put(cmd)
            except:
               sys.error("Cmd Destination {0} does not exist".format(cmd['dst']))
   time.sleep(0.01)
