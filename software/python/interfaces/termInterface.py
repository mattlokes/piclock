import signal
import zmq
from zmq.eventloop import ioloop, zmqstream
import sys
import os

##########################################################

from libraries.frameLib import *
from libraries.systemLib import *

class termInterface():

   ID="DISP"
   debugSys = False
   

   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)

   def __init__( self, cmdQueueRx, cmdQueueTx, frameQueue, **kwargs ):
      self.cmdQueueRxPath = cmdQueueRx
      self.cmdQueueTxPath = cmdQueueTx
      self.frameQueuePath = frameQueue
   
      self.sys = sysPrint(self.ID, self.debugSys)      
      
      self.context = zmq.Context()     
      self.frameQueue = self.context.socket(zmq.SUB)
      self.frameQueue.connect(self.frameQueuePath)
      self.frameQueue.setsockopt(zmq.SUBSCRIBE, '')

      self.frameStream = zmqstream.ZMQStream(self.frameQueue)
      self.frameStream.on_recv(self.__framePoll)
      
      self.cmdQueueRx = self.context.socket(zmq.SUB)
      self.cmdQueueRx.connect(self.cmdQueueRxPath)
      self.cmdQueueRx.setsockopt(zmq.SUBSCRIBE, self.ID)

      self.cmdRxStream = zmqstream.ZMQStream(self.cmdQueueRx)
      self.cmdRxStream.on_recv(self.__rxPoll)

      self.sys.info("Initializing Application...")

   def startup( self ):
      self.frameCount=0
      self.sys.info("Starting Application...")
   
   def extkill(self,signal,frame):
      self.kill()


   def kill( self ):
      self.sys.info("Stopping Application...")
      ioloop.IOLoop.instance().stop()

   def __framePoll( self , msg ):
      msgSplit = msg[0].split('#')
      cmd = {'dst': msgSplit[0], 'src': msgSplit[1], 
             'typ': msgSplit[2], 'len': msgSplit[3], 'dat': msgSplit[4]} 
         
      if cmd['typ'] == "FRAME":
         os.system('clear')
         #frameLib.debugFramePrint(frame)
         frameLib.debugFrameLetterPrint(bytearray(cmd['dat']))

   def __rxPoll( self , msg ):
      print msg
      msgSplit = msg[0].split('#')
      cmd = {'dst': msgSplit[0], 'src': msgSplit[1], 
             'typ': msgSplit[2], 'len': msgSplit[3], 'dat': msgSplit[4]} 
         
      if cmd['typ'] == "KILL" :   self.kill()

if __name__ == "__main__":
    cmdQRx = "ipc:///tmp/cmdQRx"
    cmdQTx = "ipc:///tmp/cmdQTx"
    frameQ = "ipc:///tmp/frameQ"
     
    if len(sys.argv) < 4 and len(sys.argv) > 1:
       print "Argument Error Expected 3 arguments, However got {0}".format(len(sys.argv))
    elif len(sys.argv) > 1:
       cmdQRx = sys.argv[1]
       cmdQTx = sys.argv[2]
       frameQ = sys.argv[3]

    ioloop.install()
    app = termInterface( "ipc:///tmp/cmdQRx", "ipc:///tmp/cmdQTx" , "ipc:///tmp/frameQo")
    signal.signal(signal.SIGINT, app.extkill)
    app.startup()
    ioloop.IOLoop.instance().start()
