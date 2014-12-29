import sys
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading 
import time
import re

from libraries.systemLib import *

class WSHandler( tornado.websocket.WebSocketHandler ):

   dying = False
   rxPollTime = 0.02 #50Hz

   def __init__( self, *args, **kwargs ):
      super(WSHandler,self).__init__(*args, **kwargs)

   def initialize( self, txQueue, rxQueue, debugSys, ID ):
      self.ID = ID
      self.sys = sysPrint(self.ID, debugSys)
      self.txQueue = txQueue
      self.rxQueue = rxQueue
      threading.Timer(self.rxPollTime, self.__rxPoll).start() #rxQueue Poller
   
   def check_origin( self, origin ):
      return True      
   
   def open( self ):
      self.sys.info("New Connection"),
      self.write_message("WS_IFACE")
    
   def on_message( self, message ):
      data = message
      cmdParse = re.search(r"#(.*)#(.*)#(.*)#", data)
#      print "***** {0}".format(data)
      if cmdParse is not None:
         self.txQueue.put({'src': self.ID, 'dst': cmdParse.group(1), 
                           'typ': cmdParse.group(2), 'dat': cmdParse.group(3)}) 
 #        print {'src': self.ID, 'dst': cmdParse.group(1), 'typ': cmdParse.group(2), 'dat': cmdParse.group(3)}
   def on_close( self ):
      self.sys.info("Connection Closed"),


   def __rxPoll(self):
      cmd = self.rxQueue.get()
      self.sys.rxDebug(cmd)

      # Decode Incoming Cmd Packets
      if cmd['typ'] == "KILL":
         self.kill()

      if not self.dying: threading.Timer(self.rxPollTime, self.__rxPoll).start() #rxQueue Poller


   def kill ( self ):
      self.dying = True
    
class wsInterface( threading.Thread ):
   
   ID = "WEBSOCK"
   dying = False
   
   # framePacket: { 'dst': <packetDst>, 'src': 'CLOCK'    'dat': <frameData> }
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)

   def __init__( self, txQueue, rxQueue, **kwargs ):
      threading.Thread.__init__(self) #MagicT
      self.sys = sysPrint(self.ID, kwargs['debugSys'])
      self.txQueue = txQueue
      self.rxQueue = rxQueue
      self.debugSys = kwargs['debugSys']
      self.start()
      self.sys.info("Initializing Application...")

   def startup( self ):
      self.sys.info("Starting Application...")
      self.application = tornado.web.Application([(r'/ws', WSHandler, 
      { "txQueue": self.txQueue, "rxQueue":self.rxQueue, "debugSys": self.debugSys, "ID": self.ID }),])
      self.http_server = tornado.httpserver.HTTPServer(self.application)
      self.http_server.listen(5005)
      threading.Timer(0.001, self.__tornadoStart).start() #Start Tornado frome seperate instance
   
   def __tornadoStart( self ):
      tornado.ioloop.IOLoop.instance().start()


   def kill( self ):
      self.dying = True
      tornado.ioloop.IOLoop.instance().stop()
      time.sleep(0.1)
      self.rxQueue.put({'dst':"WEBSOCK",'src':"WEBSOCK",'typ':"KILL",'dat':0}) #HACK TO KILL WSHANDLER
      self.sys.info("Stopping Application...")
