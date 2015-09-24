import serial
import signal
import zmq
from zmq.eventloop import ioloop, zmqstream
import sys
import os

##########################################################

from libraries.frameLib import *
from libraries.systemLib import *

class hwInterface():

   ID="DISP"
   debugSys = False

   fBuff =[]
   fBuffMax = 10
   fpsTime = 0.04

   ser = serial.Serial( port='/dev/ttyAMA0', baudrate=460800, rtscts=True)
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
      
      self.fBuffTicker = ioloop.PeriodicCallback(self.__fBuffPoll, (self.fpsTime * 1000))
      self.fBuffTicker.start()
      self.sys.info("Initializing Application...")

   def startup( self ):
      self.sys.info("Starting Application...")
   
   def extkill(self,signal,frame):
      self.kill()


   def kill( self ):
      self.fBuffTicker.stop()
      self.ser.close()
      self.sys.info("Stopping Application...")
      ioloop.IOLoop.instance().stop()

   def __framePoll( self , msg ):
      msgSplit = msg[0].split('#')
      cmd = {'dst': msgSplit[0], 'src': msgSplit[1], 
             'typ': msgSplit[2], 'len': msgSplit[3], 'dat': msgSplit[4]} 
         
      if cmd['typ'] == "FRAME":
         frame = bytearray(cmd['dat'])
         if len(frame) == 1024: 
            if len(self.fBuff) <= self.fBuffMax: self.fBuff.append(frame)
            else:  print "Buffer Full! Dropping Frame!"
         else:                  print "Frame not 1024 Bytes!!"

   def __fBuffPoll (self):
      self.ser.flushOutput()
      if len(self.fBuff) > 0:
         f = self.fBuff.pop(0)
         print ''.join(format(x, '02x') for x in f[0:64])
         self.ser.write(f)
                          
   def __rxPoll( self , msg ):
      print msg
      msgSplit = msg[0].split('#')
      cmd = {'dst': msgSplit[0], 'src': msgSplit[1], 
             'typ': msgSplit[2], 'len': msgSplit[3], 'dat': msgSplit[4]} 
         
      if cmd['typ'] == "KILL" :   self.kill()
      elif cmd['typ'] == "TESTPOINT":
         x = int(cmd['dat'][0:2])
         y = int(cmd['dat'][2:4])
         col = bytearray([int(cmd['dat'][4:6],16),
                          int(cmd['dat'][6:8],16),
                          int(cmd['dat'][8:10],16),
                          int(cmd['dat'][10:12],16)])
         f = bytearray(1024)
         frameLib.DrawFramePixel(f, x, y, col)
         print ''.join(format(x, '02x') for x in col)
         print ''.join(format(x, '02x') for x in f[0:64])
         print self.ser.write(f)

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
    app = hwInterface( "ipc:///tmp/cmdQRx", "ipc:///tmp/cmdQTx" , "ipc:///tmp/frameQo")
    signal.signal(signal.SIGINT, app.extkill)
    app.startup()
    ioloop.IOLoop.instance().start()
