#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#   Application Name:   Control Point
#
#             Author:   Matt
#
#       Description:   Used to keep order in the wordclock system, controls applications
#                      muxes flow of information across the various message queues,
#                      also applies a watchdog behaviour if application falls over.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import signal
import sys
import zmq
from zmq.eventloop import ioloop, zmqstream
from threading import Thread

from libraries.systemLib import *


class control():
   
   ID = "CONTROL"
   debugSys = False

   activeAppID = "CLOCK"
   
   watchPollTime = 5

   moduleRegister = {}   
   
   def __init__(self, configJson, cmdQueueRx, cmdQueueTx, adminQueue, **kwargs):
      
      self.configJson = configJson
      
      self.cmdQueueRxPath = cmdQueueRx      #Control Publisher
      self.cmdQueueTxPath = cmdQueueTx      #Control Subscriber
      self.adminQueuePath   = adminQueue    #Control REP-REQ

      self.sys = sysPrint(self.ID, self.debugSys)
      self.context = zmq.Context()
   
      self.cmdForwarder = Thread(target = self.__forwarderThread, args = (self.cmdQueueTxPath, self.cmdQueueRxPath ))
      self.frameForwarder = Thread(target = self.__forwarderThread, args = ("ipc:///tmp/frameQ", "ipc:///tmp/frameQo" ))
      self.frameForwarder.start()
      self.cmdForwarder.start()
 
      # cmdQueue Bus
      self.cmdQueueTx = self.context.socket(zmq.PUB)
      self.cmdQueueTx.connect(self.cmdQueueTxPath)

      self.cmdQueueRx = self.context.socket(zmq.SUB)
      self.cmdQueueRx.connect(self.cmdQueueRxPath)
      self.cmdQueueRx.setsockopt(zmq.SUBSCRIBE, "")
      
      self.cmdStreamRx = zmqstream.ZMQStream(self.cmdQueueRx)
      self.cmdStreamRx.on_recv(self.__cmdRxPoll)
      
      # adminQueue Bus
      #self.adminQueue = self.context.socket(zmq.REP)
      #self.adminQueue.bind(self.adminQueuePath)
      
      #self.adminStream = zmqstream.ZMQStream(self.adminQueue)
      #self.adminStream.on_recv(self.__adminPoll)

      #self.watchTicker = ioloop.PeriodicCallback(self.__watchPoll, (self.watchPollTime * 1000))
      
      self.sys.info("Initializing...")
      
   def extkill(self,signal,frame):
      self.kill()
   
   def startup(self):
      self.__registerModules( self.configJson, self.moduleRegister )
      self.sys.info("Starting...")

   def kill(self):
      #self.watchTicker.stop()
      self.sys.info("Stopping ...")
      ioloop.IOLoop.instance().stop()

   def ctlMsgHandler (self, msg ):
      print msg
      if msg[2] == "SWITCH":
         newActiveAppID = msg[4]   
         self.cmdQueueTx.send(self.__genCmd( self.activeAppID, self.ID, "PAUSE", "0"))
         self.cmdQueueTx.send(self.__genCmd( newActiveAppID,   self.ID, "RESUME", "0"))
         self.activeAppID = newActiveAppID
  
   def __cmdRxPoll( self, rawMsg ):
      # Format: DST#SRC#TYP#DATLEN#DAT
      msg = rawMsg[0].split('#')
      if msg[0] == self.ID: self.ctlMsgHandler(msg)

   def __adminPoll( self, rawMsg ):
      pass

   def __registerModules ( self, json, register ):
      pass
   
   def __genCmd( self, dst ,src, typ, dat ):
      return "{0}#{1}#{2}#{3}#{4}".format(dst,src,typ,len(dat),dat)
 
   def __forwarderThread( self, subPort, pubPort ):
      try:
         context = zmq.Context(1)
         # Socket facing clients
         frontend = context.socket(zmq.SUB)
         frontend.bind(subPort)

         frontend.setsockopt(zmq.SUBSCRIBE, "")

         # Socket facing services
         backend = context.socket(zmq.PUB)
         backend.bind(pubPort)

         zmq.device(zmq.FORWARDER, frontend, backend)
      except Exception, e:
         print e
         print "bringing down zmq device"
      finally:
         pass
         frontend.close()
         backend.close()
         context.term()

if __name__ == "__main__":
    cmdQRx   = "ipc:///tmp/cmdQRx"
    cmdQTx   = "ipc:///tmp/cmdQTx"
    adminQ   = "ipc:///tmp/adminQ"
     
    if len(sys.argv) < 4 and len(sys.argv) > 2:
       print "Argument Error Expected 3 arguments, However got {0}".format(len(sys.argv)-1)
    elif len(sys.argv) == 2:
       configJsonPath = sys.argv[1]
    elif len(sys.argv) > 2:
       configJsonPath = sys.argv[1]
       cmdQRx   = sys.argv[2]
       cmdQTx   = sys.argv[3]
       
    ioloop.install()
    ctl = control( " ", cmdQRx, cmdQTx, adminQ )
    signal.signal(signal.SIGINT, ctl.extkill)
    ctl.startup()
    print "AdminQ can be connected to at: {0}".format(adminQ)
    ioloop.IOLoop.instance().start()

   #def sendStat(self, dst):
   # stat = "|{0}|{1}|".format(self.state, float(1/self.appPollTime) )
   # self.cmdQueueTx.send("{0}#{1}#STATUS#{2}#{3}".format(dst,self.app.ID,
   #                                                       len(stat), stat))


