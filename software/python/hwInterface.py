import serial
import array
import time
import threading
from threading import Thread
from threading import Event
import signal
import sys

##########################################################

import os

class hwInterface(threading.Thread):

   frameLib= __import__('frameLib')

   #CMD TYPES 0x43
   PING_CMD 	 =  [0x43,0x00]
   START_DRAW	 =  [0x43,0x01]
   START_STREAM	 =  [0x43,0x02]
   FLUSH_BUFFERS =  [0x43,0x04]
   GET_LIGHT	 =  [0x43,0x08]
   GET_TEMP	 =  [0x43,0x10]
   
   ID="IFACE"
   dying = False
   debugEn = False
   ser = serial.Serial( '/dev/ttyAMA0', 460800)
   
   serialPollTime = 0.005
   rxCmdPollTime = 0.02
   txFramePollTime = 0.01

   srtThreadAlive = False
   srtBuffer =[ ]
   srtFlagAck=0
   srtThreadEvent = Event()
   srt = Thread(target = __serialRecieverThread, args = (srtThreadEvent, "SRT", ))
   srdpt = Thread(target = __serialRecieverDataParseThread, args = (srtThreadEvent, "SRDPT", ))
 
   frameCount=0
   
   # framePacket: { 'dst': <packetDst>, 'src': 'CLOCK'    'dat': <frameData> }
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # rxFrameQueue = RX Frame Queue, (Always Pop)
   # txCmdQueue = TX Cmd Queue , (Always Push)
   # rxCmdQueue = Rx Cmd Queue , (Always Pop)

   def __init__(self,txFrameQueue,txCmdQueue,rxCmdQueue):
      threading.Thread.__init__(self) #MagicT
      self.dying = False
      self.rxFrameQueue = rxFrameQueue
      self.txCmdQueue = txCmdQueue
      self.rxCmdQueue = rxCmdQueue
      threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller
      self.start()

   def startup(self):
      self.frameCount=0
      self.srtThreadAlive = True
      self.srt.start()
      self.srdpt.start()
      threading.Timer(self.txFramePollTime, self.__txFramePoll).start() #frameQueue Poller


   def kill(self):
      self.dying = True
      self.srtThreadEvent.set()
      self.srtThreadAlive = 0
      self.ser.close()
      time.sleep(0.1)
      self.stop()
      print "Stopping {0} Application..."

   def __txFramePoll(self):
      if not self.txFrameQueue.empty():
         fr = self.txFrameQueue.get()
         # Send Stream REQ
         self.__serialSendBytes(self.START_STREAM)
         
         # Wait for ACK
         self.srtThreadEvent.set()
         while(self.srtFlagAck == 0): time.sleep(self.serialPollTime)
         self.srtFlagAck=0
         self.srtThreadEvent.clear()
         
         #os.system('clear')
         #print "Frame #{0}".format(str(self.frameCount))
         
         #Send Frame
         self.__serialSendFrame(fr['dat'])
         self.frameCount+=1
         
         #Wait for Ack
         self.srtThreadEvent.set()
         while(self.srtFlagAck == 0): time.sleep(self.serialPollTime)
         self.srtFlagAck=0
         self.srtThreadEvent.clear()

      if not self.dying: threading.Timer(self.txFramePollTime, self.__txFramePoll).start() #rxCmdQueue Poller
   
   def __rxCmdPoll(self):
      while not self.rxCmdQueue.empty():
         # Decode Incoming Cmd Packets
         pass
      if not self.dying: threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller
   
   def __serialSendBytes( self, b ):
       for i in b:
           self.ser.write(chr(i))
   
   def __serialSendFrame( self, frame ):
       outBuff = []
       for i in range(0,256):
          outBuff += [frame[i][0], frame[i][1] & 0xF0, frame[i][1] & 0x0F, frame[i][2]]
       self.ser.write(bytearray(outBuff))
   
   
   def __serialRecieverThread( self, e, name ):
       while (self.srtThreadAlive):
          e.wait()
          time.sleep(self.serialPollTime)
          while (self.ser.inWaiting() != 0):
              self.srtBuffer.append(self.ser.read())
   
   def __serialRecieverDataParseThread ( self, e, name ):
      while (self.srtThreadAlive):
         e.wait()
         time.sleep(self.serial.PollTime)
         while len(self.srtBuffer) > 0:
            tmpStr = ""
            #Response Message Parse
            if self.srtBuffer[0] == 'R':
               while len(self.srtBuffer) < 4: pass
               if self.srtBuffer[1] == "\x01":
                  self.srtFlagAck=1
               for i in range(0,4):
                  if ord(self.srtBuffer[0]) > 31:
                     tmpStr+= self.srtBuffer.pop(0) #Letter
                  else:
                     tmpStr+= str(ord(self.srtBuffer.pop(0))) #Num
            #Debug Message Parse
            elif self.srtBuffer[0] == 'D':
               debug_rx=True
               while debug_rx:
                  if len(self.srtBuffer) > 0: 
                     if self.srtBuffer[0] != '\n':
                         tmpStr+= self.srtBuffer.pop(0)
                     else:
                        self.srtBuffer.pop(0)
                        debug_rx=False
            #None Standard Type Packet
            else:
               tmpStr="SRT-PARSER: PARSE ERROR"
               self.srtBuffer.pop(0)
               print self.srtBuffer
            if self.debugEn:  print tmpStr
