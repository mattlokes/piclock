import sys
import signal
import os

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

class WSHandler( tornado.websocket.WebSocketHandler ):

   def __init__( self, *args, **kwargs ):
      super(WSHandler,self).__init__(*args, **kwargs)

   def initialize( self, parent, ID , txFifo ):
      self.txFifo = txFifo
      self.parent = parent
      self.ID = ID
   
   def check_origin( self, origin ):
      return True      
   
   def checkTxFifo( self ):
      if len(self.txFifo) > 0:
         data = self.txFifo.popleft()
         frame_data = data[0].split('#')[4].encode('hex')
         #Strip Alpha data out , saves bandwidth and not used yet.
         frame_data_stripped = ""
         for i in range (0, 256):
            frame_data_stripped += frame_data[(8*i+2) : (8*i+8)]
         self.write_message(frame_data_stripped)

   def open( self ):
      print "Connection Opened"
      #self.write_message("WS_IFACE")
      self.txChecker = ioloop.PeriodicCallback( self.checkTxFifo, 20)
      self.txChecker.start()
    
   def on_message( self, message ):
      print "Disp got a message.... thats not right...."
   def on_close( self ):
      print "Connection Closed"
      self.txChecker.stop()

class wsInterface( threading.Thread ):
   
   ID = "DISP"
   
   # framePacket: { 'dst': <packetDst>, 'src': 'CLOCK'    'dat': <frameData> }
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)

   def __init__( self, frameQueue, **kwargs ):
      self.txFifo = deque()

      self.frameQueuePath = frameQueue     
 
      self.context = zmq.Context()     
      
      self.frameQueue = self.context.socket(zmq.SUB)
      self.frameQueue.connect(self.frameQueuePath)
      self.frameQueue.setsockopt(zmq.SUBSCRIBE, '')

      self.frameStream = zmqstream.ZMQStream(self.frameQueue)
      self.frameStream.on_recv(self.__framePoll)

   def __framePoll ( self, msg):
      self.txFifo.append(msg)
   
   def startup( self ):
      self.application = tornado.web.Application([(r'/ws', WSHandler, 
      { "parent": self, "ID": self.ID, "txFifo": self.txFifo }),])
      self.http_server = tornado.httpserver.HTTPServer(self.application)
      self.http_server.listen(8855)
    #  threading.Timer(0.001, self.__tornadoStart).start() #Start Tornado frome seperate instance
   
    #def __tornadoStart( self ):
    #  tornado.ioloop.IOLoop.instance().start()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.environ['PYTHONPATH']+"/displays/webDisplay/webDisplay.html", title="webDisplay")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    frameQ = "ipc:///tmp/frameQo"
     
    #ioloop.install()
    wsApp = wsInterface( frameQ )
    wsApp.startup()
    print "Websocket Server at 127.0.0.1:8855/ws ..."

    serveApp = make_app()
    serveApp.listen(8080)
    print "Webpage being served at 127.0.0.1:8080/ ..."
    #ioloop.IOLoop.instance().start()
    #tornado.ioloop.IOLoop.current().start()
    tornado.ioloop.IOLoop.instance().start()
