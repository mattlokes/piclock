import serial
import array
import time
import threading
from threading import Thread
from threading import Event
import signal

##########################################################

import os
from libraries.frameLib import *
from libraries.systemLib import *

class hwInterface( threading.Thread ):

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
   rxPollTime = 0.01

   srtThreadAlive = False
   srtBuffer =[]
   srtFlagAck=0
   srtThreadEvent = Event()
 
   frameCount=0
   
   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }

   # txQueue = TX Cmd Queue , (Always Push)
   # rxQueue = Rx Cmd Queue , (Always Pop)

   def __init__( self, txQueue, rxQueue, fastRx, fakeSerial, debugSys ):
      threading.Thread.__init__( self ) #MagicT
      self.sys = sysPrint(self.ID, debugSys)
      self.txQueue = txQueue
      self.rxQueue = rxQueue
      self.fastRx = fastRx
      self.fakeSerial = fakeSerial
      self.debugSys = debugSys
      if not self.fakeSerial:
         self.ser = serial.Serial( '/dev/ttyAMA0', 460800)
      #When using debugging turn fastRx off as it turns on the serial parsing threads
      if not self.fastRx:
         self.srt = Thread(target = self.__serialRecieverThread, args = (self.srtThreadEvent, "SRT", ))
         self.srdpt = Thread(target = self.__serialRecieverDataParseThread, args = (self.srtThreadEvent, "SRDPT", ))
      self.start()
      self.sys.info("Initializing Application...")

   def startup( self ):
      self.frameCount=0
      if not self.fastRx:
         self.sys.info("fastRx disabled, serial parsing threads starting")
         self.srtThreadAlive = True
         self.srt.start()
         self.srdpt.start()
      threading.Timer(self.rxPollTime, self.__rxPoll).start() #rxQueue Poller
      self.sys.info("Starting Application...")


   def kill( self ):
      self.dying = True
      if not self.fastRx:
         self.srtThreadEvent.set()
         self.srtThreadAlive = 0
      if not self.fakeSerial:
         self.ser.close()
      time.sleep(0.1)
      self.sys.info("Stopping Application...")

   def __rxPoll( self ):
      cmd = self.rxQueue.get()
      self.sys.rxDebug(cmd)

      #Decode Packets
      #Frame Data, Send to Display
      if cmd['typ'] == "FRAME":
         self.__serialSendBytes(self.START_STREAM) # Send Stream REQ
         self.__serialWaitAck()   # Wait for ACK        

         #os.system('clear')
         #print "Frame #{0}".format(str(self.frameCount))
         
         self.__serialSendFrame(cmd['dat']) #Send Frame
         self.__serialWaitAck() # Wait for ACK          
         
         self.frameCount+=1

      #Kill Command, Stop Module
      if cmd['typ'] == "KILL":
         self.kill() 

      if not self.dying: threading.Timer(self.rxPollTime, self.__rxPoll).start() #rxQueue Poller
   
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

   def __serialWaitAck ( self ):
      if self.fakeSerial:
         pass
      else:
         if not self.fastRx:
            self.srtThreadEvent.set()
            while(self.srtFlagAck == 0): time.sleep(self.serialPollTime)
            self.srtFlagAck=0
            self.srtThreadEvent.clear()
         else:
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
               self.sys.debug(self.srtBuffer)
            if self.debugEn:  self.sys.debug(tmpStr)
