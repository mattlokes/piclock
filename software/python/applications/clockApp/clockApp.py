#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#          Application Name:   Clock
#                    Author:   Matt
#
#               Description:   Clock Application using the basic functionality 
#                              of the LED Grid.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import Queue
import threading
import time
import datetime

from libraries.frameLib import *

class clockApp(threading.Thread):
   
   #Import Constants for Fonts and Words
   from clockAppConsts import *  
 
   ID = "CLOCK"
   dying = False
   appPollTime = 0.1    #10Hz
   rxCmdPollTime = 0.02 #50Hz  
   forceUpdate = False

   clockMode = "word0"
   #clockMode = "dig2"
   #clockMode = "dig1"
   #clockMode = "dig0"
   
   frame = []
   timeColour = [0x00,0xFF,0x00]  #Default Colour
   #timeColour = [0x12,0xD7,0xFF]  #Default Colour
   timeHistory=""

   # cmdPacket:   { 'dst': 'CLOCK',     'src':<packetSrc> 'typ': <cmdType>, 'dat': <cmdData> }
  
   # txCmdQueue = TX Cmd Queue , (Always Push)
   # rxCmdQueue = Rx Cmd Queue , (Always Pop)
  
   def __init__(self,txCmdQueue,rxCmdQueue):
      threading.Thread.__init__(self) #MagicT
      self.txCmdQueue = txCmdQueue
      self.rxCmdQueue = rxCmdQueue
      self.start()
      print "Initializing {0} Application...".format(self.ID)

   def startup(self):
      frameLib.CreateBlankFrame(self.frame)
      self.forceUpdate = True
      threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller
      threading.Timer(self.appPollTime, self.__appPoll).start() #App Poller
      print "Starting {0} Application...".format(self.ID)


   def kill(self):
      self.dying = True
      time.sleep(0.1)
      #self.stop()
      print "Stopping {0} Application...".format(self.ID)

   def __rxCmdPoll(self):
      cmd = self.rxCmdQueue.get()
      # Decode Incoming Cmd Packets
      #print "-- {0} -- {1} --".format(cmd['typ'],cmd['dat'])
      # Colour Change Command
      if cmd['typ'] == "COLOR":
         self.timeColour = [int(cmd['dat'][4:6],16), #R
                            int(cmd['dat'][2:4],16), #G
                            int(cmd['dat'][0:2],16)] #B
         self.forceUpdate = True
      # Time Format Change
      elif cmd['typ'] == "MODE":
         self.forceUpdate = True

      if not self.dying: threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller

   # Main Application Loop
   def __appPoll(self):
      #Update Time
      get_h = datetime.datetime.now().time().hour
      get_m = datetime.datetime.now().time().minute
      timeHistoryCompare=str(get_h)+str(get_m)

      if self.timeHistory != timeHistoryCompare or self.forceUpdate:
         frameLib.CreateBlankFrame(self.frame)
         self.__CreateTimeFrame( self.frame, get_h, get_m, self.clockMode, self.timeColour )
         self.__framePush(self.frame)
         self.timeHistory=timeHistoryCompare
         self.forceUpdate = False
      
      if not self.dying: threading.Timer(self.appPollTime, self.__appPoll).start() #App Poller
   
   def __framePush(self, frame):
      self.txCmdQueue.put({'dst': "DISP",
                           'src': self.ID,
                           'typ': "frame",
                           'dat': frame})
   
   def __CreateTimeFrame(self, frame, hour, mins, mode, colour ):
      if mode == "word0":
         self.__CreateWordTimeFrame(frame, hour, mins, colour, 0)
      if mode == "dig0":
         self.__CreateDigitalTimeFrame(frame, hour, mins, colour)
      if mode == "dig2":
         self.__CreateMegaDigitalTimeFrame(frame, hour, mins, colour)
   
   def __CreateDigitalTimeFrame(self, frame, hour, mins, colour):
      font_size = (5,3)
      font_space = 1
      char = [hour / 10, hour % 10, mins / 10, mins % 10]
      ptr_x = 0
      ptr_y = 5
      for ci in range(0,len(char)):
         c = char[ci]
         for i in range(0,font_size[0]):
            for j in range(0,font_size[1]):
               if self.DIGNUM_5_3[c][(i*font_size[1])+j] == 1:
                  frameLib.DrawFramePixel(frame, ptr_x+j, ptr_y+i, colour)
         if ci == 1: ptr_x += 1 #add extra space for mins to hours
         ptr_x += font_size[1]+font_space
   
   def __CreateMegaDigitalTimeFrame(self, frame, hour, mins, colour):
      font_size = (8,5)
      font_space = 1
      char = [hour / 10, hour % 10,10, mins / 10, mins % 10]
      ptr_x = 0
      ptr_y = 0
      for ci in range(0,len(char)):
         c = char[ci]
         for i in range(0,font_size[0]):
            for j in range(0,font_size[1]):
               if self.DIGNUM_8_5[c][(i*font_size[1])+j] == 1:
                  frameLib.DrawFramePixel(frame, ptr_x+j, ptr_y+i, colour)
         ptr_x += font_size[1]+font_space
         if ci == 2: # After Colon Jump Next Line
            ptr_x = 5
            ptr_y = 9 
   
   def __CreateWordTimeFrame(self, frame, hour, mins, colour, subMode):
      #PRE TIME
      for word in self.PRE_TIME[1]:
         frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #MIN_NUM
      if (mins > 30): m = 60 - mins
      else: m = mins
      for word in self.MIN_NUM[m]:
         frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #Alter hour when  mins to
      if mins > 30:
         if hour == 24: hour = 1
         else: hour += 1    
 
      #MIN_WORDS
      if mins != 0:
         if (mins > 30):
            if mins == 45: mw = 3 #TO
            else: mw = 1          #MINS TO
         else:
            if mins == 15 or mins == 30: mw = 2  #PAST
            else: mw = 0                        #MINS PAST
         for word in self.MIN_WORDS[mw]:
            frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #HOUR_NUM
      if (hour > 12): h = hour - 12
      else: h = hour
      for word in self.HOUR_NUM[h]:
         frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #TOD_WORDS
      if subMode == "1":
         if (hour < 12): tod = 2
         elif ( hour < 18): tod = 3
         elif ( hour < 21): tod = 4
         else: tod = 5
         for word in self.TOD_WORDS[tod]:
            frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)

