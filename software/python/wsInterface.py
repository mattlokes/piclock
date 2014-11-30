import sys
import commands
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading 
import time
import re
from collections import deque 

class WSHandler(tornado.websocket.WebSocketHandler):
   def __init__(self, *args, **kwargs):
      super(WSHandler,self).__init__(*args, **kwargs)

   def initialize(self, txCmdQueue, ID ):
      self.fifo = txCmdQueue
      self.ID = ID
   
   def check_origin(self, origin):
      return True      
   
   def open(self):
       print ('New Connection'),
       self.write_message("WS_IFACE")
    
   def on_message(self, message):
       data = message
       cmdParse = re.search(r"#(.*)#(.*)#(.*)#", data)
       if cmdParse is not None:
          self.fifo.put({'src': self.ID, 'dst': cmdParse.group(1), 
                         'typ': cmdParse.group(2), 'dat': cmdParse.group(3)}) 

   def on_close(self):
      print 'Connection Closed'
    
class wsInterface(threading.Thread):
   
   ID = "WSINTER"
   dying = False
   
   # framePacket: { 'dst': <packetDst>, 'src': 'CLOCK'    'dat': <frameData> }
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # txCmdQueue = TX Cmd Queue , (Always Push)
   # rxCmdQueue = Rx Cmd Queue , (Always Pop)

   def __init__(self,txCmdQueue):
      threading.Thread.__init__(self) #MagicT
      self.dying = False
      self.txCmdQueue = txCmdQueue
      #self.rxCmdQueue = rxCmdQueue
      #threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller
      self.start()
      print "Initializing {0} Application...".format(self.ID)

   def startup(self):
      print "Starting {0} Application...".format(self.ID)
      self.application = tornado.web.Application([(r'/ws', WSHandler, 
      { "txCmdQueue": self.txCmdQueue , "ID": self.ID}),])
      self.http_server = tornado.httpserver.HTTPServer(self.application)
      self.http_server.listen(5005)
      threading.Timer(0.001, self.__tornadoStart).start() #Start Tornado frome seperate instance
   
   def __tornadoStart(self):
      tornado.ioloop.IOLoop.instance().start()


   def kill(self):
      self.dying = True
      tornado.ioloop.IOLoop.instance().stop()
      time.sleep(0.1)
      print "Stopping {0} Application...".format(self.ID)
