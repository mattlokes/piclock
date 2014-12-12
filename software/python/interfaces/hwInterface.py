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
from libraries.frameLib import *

class hwInterface(threading.Thread):

   #CMD TYPES 0x43
   PING_CMD 	 =  [0x43,0x00]
   START_DRAW	 =  [0x43,0x01]
   START_STREAM	 =  [0x43,0x02]
   FLUSH_BUFFERS =  [0x43,0x04]
   GET_LIGHT	 =  [0x43,0x08]
   GET_TEMP	 =  [0x43,0x10]
   
   ID="DISP"
   dying = False
   debugEn = False
   
   serialPollTime = 0.005
   rxCmdPollTime = 0.01

   srtThreadAlive = False
   srtBuffer =[]
   srtFlagAck=0
   srtThreadEvent = Event()
 
   frameCount=0
   
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # txCmdQueue = TX Cmd Queue , (Always Push)
   # rxCmdQueue = Rx Cmd Queue , (Always Pop)

   def __init__(self,txCmdQueue,rxCmdQueue,fastRx, fakeSerial):
      threading.Thread.__init__(self) #MagicT
      self.dying = False
      self.txCmdQueue = txCmdQueue
      self.rxCmdQueue = rxCmdQueue
      self.fastRx = fastRx
      self.fakeSerial = fakeSerial
      if not self.fakeSerial:
         ser = serial.Serial( '/dev/ttyAMA0', 460800)
      #When using debugging turn fastRx off as it turns on the serial parsing threads
      if not self.fastRx:
         self.srt = Thread(target = self.__serialRecieverThread, args = (self.srtThreadEvent, "SRT", ))
         self.srdpt = Thread(target = self.__serialRecieverDataParseThread, args = (self.srtThreadEvent, "SRDPT", ))
      self.start()
      print "Initializing {0} Application...".format(self.ID)

   def startup(self):
      self.frameCount=0
      if not self.fastRx:
         print "hwInterface: fastRx disabled, serial parsing threads start"
         self.srtThreadAlive = True
         self.srt.start()
         self.srdpt.start()
      threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller
      print "Starting {0} Application...".format(self.ID)


   def kill(self):
      self.dying = True
      if not self.fastRx:
         self.srtThreadEvent.set()
         self.srtThreadAlive = 0
      if not self.fakeSerial:
         self.ser.close()
      time.sleep(0.1)
      #self.stop()
      print "Stopping {0} Application...".format(self.ID)

   def __rxCmdPoll(self):
      cmd = self.rxCmdQueue.get()
      if cmd['typ'] == "frame":
         self.__serialSendBytes(self.START_STREAM) # Send Stream REQ
         self.__serialWaitAck()   # Wait for ACK        

         #os.system('clear')
         #print "Frame #{0}".format(str(self.frameCount))
         
         self.__serialSendFrame(cmd['dat']) #Send Frame
         self.__serialWaitAck() # Wait for ACK          
         
         self.frameCount+=1

      if not self.dying: threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxFrameQueue Poller
   
   def __serialSendBytes( self, b ):
      if self.fakeSerial:
         pass
      else:
         for i in b:
            self.ser.write(chr(i))
   
   def __serialSendFrame( self, frame ):
      if self.fakeSerial:
         os.system('clear')
         #frameLib.debugFramePrint(frame)
         frameLib.debugFrameLetterPrint(frame)
      else:
         outBuff = []
         for i in range(0,256):
            outBuff += [frame[i][0], frame[i][1] & 0xF0, frame[i][1] & 0x0F, frame[i][2]]
         self.ser.write(bytearray(outBuff))

   def __serialWaitAck (self):
      if self.fakeSerial:
         pass
      else:
         if not self.fastRx:
            self.srtThreadEvent.set()
            while(self.srtFlagAck == 0): time.sleep(self.serialPollTime)
            self.srtFlagAck=0
            self.srtThreadEvent.clear()
         else:
            #while(self.ser.read(size=4) is not 
            self.ser.read(size=4)
   
   def __serialRecieverThread( self, e, name ):
      while (self.srtThreadAlive):
         e.wait()
         time.sleep(self.serialPollTime)
         if self.srtThreadAlive:
            while (self.ser.inWaiting() != 0):
               self.srtBuffer.append(self.ser.read())
   
   def __serialRecieverDataParseThread ( self, e, name ):
      while (self.srtThreadAlive):
         e.wait()
         time.sleep(self.serialPollTime)
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
