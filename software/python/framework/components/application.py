#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#   Application Name:   Base Application Object
#             Author:   Matt
#
#       Description:   Used to Perform Application Tasks
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import Queue
import threading

from libraries.systemLib import *

class application(threading.Thread):
   
   ID = "DEFAULT"

   appPollTime = 0.02    #50Hz
   rxPollTime = 0.02     #50Hz  
   
   state = "NONE"

   dying = False
   pauseApp = False
   debugSys = False

   # cmdPacket:   { 'dst': <packetDst>, 'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }
  
   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)
  
   def __init__(self, appClass, txQueue, rxQueue, **kwargs):
      threading.Thread.__init__(self) #MagicT
      self.txQueue = txQueue
      self.rxQueue = rxQueue

      if isinstance(kwargs, dict):
         self.app = appClass(self, **kwargs)
         if "debugSys" in kwargs.keys():
            self.debugSys = kwargs['debugSys']
      else:
         self.app = appClass(parent=self)
      
      if hasattr(self.app, 'appPollTime'): self.appPollTime = self.app.appPollTime
      if hasattr(self.app, 'rxPollTime'): self.rxPollTime = self.app.rxPollTime

      self.sys = sysPrint(self.app.ID, self.debugSys)
      self.start()
      self.sys.info("Initializing Application...")

   def startup(self):
     
      self.app.startup()
      
      if self.rxQueue != None: threading.Timer(self.rxPollTime, self.__rxPoll).start() #rx Poller
      if hasattr(self.app, 'appPollTime'): self.appPollTime = self.app.appPollTime
      threading.Timer(self.appPollTime, self.__appPoll).start() #App Poller
      self.sys.info("Starting Application...")


   def kill(self):
      self.dying = True
      self.sys.info("Stopping Application...")

   def pause(self):
      self.pauseApp = True

   def resume(self):
      self.pauseApp = False
      if hasattr(self.app, 'appPollTime'): self.appPollTime = self.app.appPollTime
      threading.Timer(self.appPollTime, self.__appPoll).start() #App Poller

   def __rxPoll(self):
      if not self.dying:
         cmd = self.rxQueue.get()
         self.sys.rxDebug(cmd)

         self.app.incomingRx(cmd)
         
         if not self.dying: threading.Timer(self.rxPollTime, self.__rxPoll).start() #rxQueue Poller

   # Main Application Loop
   def __appPoll(self):
      if not self.dying and not self.pauseApp:
        
          msgs = self.app.appTick()
          if msgs != None:
             for msg in msgs:
                self.txQueue.put(msg)
         
          if not self.dying and not self.pauseApp:
             if hasattr(self.app, 'appPollTime'): self.appPollTime = self.app.appPollTime
             threading.Timer(self.appPollTime, self.__appPoll).start() #App Poller
