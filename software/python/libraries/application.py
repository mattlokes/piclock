#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#   Application Name:   Base Application Object
#             Author:   Matt
#
#       Description:   Used to Perform Application Tasks
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import zmq
from zmq.eventloop import ioloop, zmqstream

from libraries.systemLib import *


class application():
   
   ID = "DEFAULT"

   appPollTime = 0.02    #50Hz
   
   state = "NONE"

   debugSys = False
   
   # cmdPacket:   { 'dst': <packetDst>, 'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }
  
   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)
  
   def __init__(self, appClass, cmdQueueRx, cmdQueueTx, frameQueue, **kwargs):
      self.cmdQueueRxPath = cmdQueueRx
      self.cmdQueueTxPath = cmdQueueTx
      self.frameQueuePath = frameQueue

      if isinstance(kwargs, dict):
         self.app = appClass(self, **kwargs)
         if "debugSys" in kwargs.keys():
            self.debugSys = kwargs['debugSys']
      else:
         self.app = appClass(parent=self)
      
      if hasattr(self.app, 'appPollTime'): self.appPollTime = self.app.appPollTime

      self.sys = sysPrint(self.app.ID, self.debugSys)
      self.context = zmq.Context()
    
      self.frameQueue = self.context.socket(zmq.PUB)
      self.frameQueue.connect(self.frameQueuePath)
      
      self.cmdQueueTx = self.context.socket(zmq.PUB)
      self.cmdQueueTx.connect(self.cmdQueueTxPath)
      
      self.cmdQueueRx = self.context.socket(zmq.SUB)
      self.cmdQueueRx.connect(self.cmdQueueRxPath)
      self.cmdQueueRx.setsockopt(zmq.SUBSCRIBE, self.app.ID)
      
      self.cmdStreamRx = zmqstream.ZMQStream(self.cmdQueueRx)
      self.cmdStreamRx.on_recv(self.__rxPoll)
      
      self.appTicker = ioloop.PeriodicCallback(self.__appPoll, (self.appPollTime * 1000))
      self.appTicker.stop()
      
      self.state = "INIT"
      self.sys.info("Initializing Application...")

   def extkill(self,signal,frame):
      self.kill()
   
   def startup(self):
      self.app.startup()
      self.state = "PAUSED"
      self.sys.info("Starting Application...")


   def kill(self):
      self.appTicker.stop()
      self.state = "DEAD"
      self.sys.info("Stopping Application...")
      ioloop.IOLoop.instance().stop() 

   def pause(self):
      self.state = "PAUSED"
      self.appTicker.stop()

   def resume(self):
      self.app.forceUpdate = True
      # appPollTime has changed so update appTicker
      if hasattr(self.app, 'appPollTime'):
          if self.appPollTime != self.app.appPollTime:
              self.appPollTime = self.app.appPollTime
              self.appTicker.callback_time = self.appPollTime * 1000
      self.state = "RUNNING"
      self.appTicker.start()

   def sendStat(self, dst):
      stat = "|{0}|{1}|".format(self.state, float(1/self.appPollTime) )
      self.cmdQueueTx.send("{0}#{1}#STATUS#{2}#{3}".format(dst,self.app.ID,
                                                           len(stat), stat))
   def changeAppTick(self, tick):
      self.pause()
      if hasattr(self.app, 'appPollTime'):
         self.app.appPollTime = float(tick)
      else:
         self.appPollTime = float(tick)
      self.resume()

   def framePush(self, dst, frame):
      self.frameQueue.send("{0}#{1}#FRAME#{2}#{3}".format(dst,self.app.ID, 
                                                          len(frame) ,str(frame)))

   def __rxPoll(self, msg):
      # Format: DST#SRC#TYP#DATLEN#DAT
      print msg[0]
      msgSplit = msg[0].split('#')
      cmd = {'dst': msgSplit[0], 'src': msgSplit[1], 
             'typ': msgSplit[2], 'len': msgSplit[3], 'dat': msgSplit[4]} 
      self.sys.rxDebug(cmd)
         
      if   cmd['typ'] == "PAUSE":   self.pause()
      elif cmd['typ'] == "KILL" :   self.kill()
      elif cmd['typ'] == "RESUME":  self.resume()
      elif cmd['typ'] == "STATUS":  self.sendStat(cmd['src'])
      elif cmd['typ'] == "APPTICK": self.changeAppTick(cmd['dat'])
      elif cmd['typ'] == "REFRESH": self.app.forceUpdate = True
      else:                         self.app.incomingRx(cmd)
         

   # Main Application Loop
   def __appPoll(self):
      #print "App Poll....."
      self.app.appTick()
