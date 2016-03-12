import sys
import signal

import zmq
from zmq.eventloop import ioloop, zmqstream

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading 
import time
import re
from collections import deque

from libraries.systemLib import *

class WSHandler( tornado.websocket.WebSocketHandler ):

   def __init__( self, *args, **kwargs ):
      super(WSHandler,self).__init__(*args, **kwargs)

   def initialize( self, parent, debugSys, ID , txFifo ):
      self.txFifo = txFifo
      self.parent = parent
      self.ID = ID
      self.sys = sysPrint(self.ID, debugSys)
   
   def check_origin( self, origin ):
      return True      
   
   def checkTxFifo( self ):
      if len(self.txFifo) > 0:
         data = self.txFifo.popleft()
         self.write_message(data[0])

   def open( self ):
      self.sys.info("New Connection"),
      self.write_message("WS_IFACE")
      self.txChecker = ioloop.PeriodicCallback( self.checkTxFifo, 20)
      self.txChecker.start()
    
   def on_message( self, message ):
      data = message
      cmdParse = re.search(r"#(.*)#(.*)#(.*)#", data)
      #print "***** {0}".format(data)
      if cmdParse is not None:
         self.parent.txHandler(r"{0}#{1}#{2}#{3}#{4}".format(cmdParse.group(1), self.ID, 
                                                      cmdParse.group(2), len(cmdParse.group(3)),
                                                      cmdParse.group(3) ) )
   def on_close( self ):
      self.sys.info("Connection Closed")
      self.txChecker.stop()

class wsInterface( threading.Thread ):
   
   ID = "WEBSOCK"
   
   # framePacket: { 'dst': <packetDst>, 'src': 'CLOCK'    'dat': <frameData> }
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)

   def __init__( self, cmdQueueRx, cmdQueueTx, **kwargs ):
      self.txFifo = deque()

      self.cmdQueueRxPath = cmdQueueRx
      self.cmdQueueTxPath = cmdQueueTx
      
      self.sys = sysPrint(self.ID, kwargs['debugSys'])
      
      self.context = zmq.Context()     
      
      self.cmdQueueTx = self.context.socket(zmq.PUB)
      self.cmdQueueTx.connect(self.cmdQueueTxPath)
      
      self.cmdQueueRx = self.context.socket(zmq.SUB)
      self.cmdQueueRx.connect(self.cmdQueueRxPath)
      self.cmdQueueRx.setsockopt(zmq.SUBSCRIBE, self.ID)

      self.cmdRxStream = zmqstream.ZMQStream(self.cmdQueueRx)
      self.cmdRxStream.on_recv(self.__rxPoll)

      self.debugSys = kwargs['debugSys']
      self.sys.info("Initializing Application...")

   def __rxPoll ( self, msg):
      #print msg
      self.txFifo.append(msg)
   
   def startup( self ):
      self.sys.info("Starting Application...")
      self.application = tornado.web.Application([(r'/ws', WSHandler, 
      { "parent": self, "debugSys": self.debugSys, "ID": self.ID, "txFifo": self.txFifo }),])
      self.http_server = tornado.httpserver.HTTPServer(self.application)
      self.http_server.listen(5005)
    #  threading.Timer(0.001, self.__tornadoStart).start() #Start Tornado frome seperate instance
   
    #def __tornadoStart( self ):
    #  tornado.ioloop.IOLoop.instance().start()

   def txHandler ( self, msg ):
      self.cmdQueueTx.send(msg)
   
   def extkill ( self, signal, frame):
      self.kill()

   def kill( self ):
      tornado.ioloop.IOLoop.instance().stop()
      self.sys.info("Stopping Application...")

if __name__ == "__main__":
    wsQRx = "ipc:///tmp/cmdQRx"
    wsQTx = "ipc:///tmp/cmdQTx"
     
    if len(sys.argv) < 3 and len(sys.argv) > 1:
       print "Argument Error Expected 2 arguments, However got {0}".format(len(sys.argv))
    elif len(sys.argv) > 1:
       cmdQRx = sys.argv[1]
       cmdQTx = sys.argv[2]

    #ioloop.install()
    app = wsInterface( "ipc:///tmp/cmdQRx", "ipc:///tmp/cmdQTx" , debugSys=False)
    signal.signal(signal.SIGINT, app.extkill)
    app.startup()
    #ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.instance().start()
