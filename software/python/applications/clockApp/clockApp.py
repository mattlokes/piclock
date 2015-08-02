#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#          Application Name:   Clock
#                    Author:   Matt
#
#               Description:   Clock Application using the basic functionality 
#                              of the LED Grid.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import datetime
import copy

from framework.components.application import *

from libraries.frameLib import *
from libraries.systemLib import *

class clockApp():
   
   #Import Constants for Fonts and Words
   from clockAppConsts import *  
 
   ID = "CLOCK"
   appPollTime = 0.1    #10Hz
   rxPollTime = 0.02 #50Hz  
   
   forceUpdate = False

   clockMode = "WORD"
   todMode = 0
   
   frame = []
   timeColour = [0x00,0xFF,0x00]  #Default Colour
   #timeColour = [0x12,0xD7,0xFF]  #Default Colour
   timeHistory=""

   def __init__(self, parent, **kwargs):
      self.parent = parent

   def startup(self):
      #frameLib.CreateBlankFrame(self.frame)
      self.forceUpdate = True

   def incomingRx ( self, cmd ):
      # Decode Incoming Cmd Packets
      # Colour Change Command
      if cmd['typ'] == "COLOR":
         self.timeColour = [int(cmd['dat'][4:6],16), #R
                            int(cmd['dat'][2:4],16), #G
                            int(cmd['dat'][0:2],16)] #B
         self.forceUpdate = True
      
      # Time Format Change
      if cmd['typ'] == "MODE":
         self.clockMode = cmd['dat']
         self.forceUpdate = True

      if cmd['typ'] == "TOD":
         if cmd['dat'] == "SUFFIX": self.todMode = 1
         elif cmd['dat'] == "AMPM": self.todMode = 2
         else:                      self.todMode = 0
         
         self.forceUpdate = True

   # Main Application Loop
   def appTick(self):
      #Update Time
      get_h = datetime.datetime.now().time().hour
      get_m = datetime.datetime.now().time().minute
      timeHistoryCompare=str(get_h)+str(get_m)

      if self.timeHistory != timeHistoryCompare or self.forceUpdate:
         tmpFrame = []
         frameLib.CreateBlankFrame(tmpFrame)
         self.CreateTimeFrame( tmpFrame, get_h, get_m, self.clockMode, self.timeColour )
         self.frame = copy.deepcopy(tmpFrame)
         self.framePush(self.frame)
         self.timeHistory=timeHistoryCompare
         self.forceUpdate = False
   
   def framePush(self, frame):
      self.parent.txQueue.put({'dst': "DISP",
                               'src': self.ID,
                               'typ': "FRAME",
                               'dat': frame})
   
   def CreateTimeFrame(self, frame, hour, mins, mode, colour ):
      if mode == "WORD":
         self.CreateWordTimeFrame(frame, hour, mins, colour, self.todMode)
      if mode == "DIG0":
         self.CreateDigitalTimeFrame(frame, hour, mins, colour)
      if mode == "DIG2":
         self.CreateMegaDigitalTimeFrame(frame, hour, mins, colour)
   
   def CreateDigitalTimeFrame(self, frame, hour, mins, colour):
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
   
   def CreateMegaDigitalTimeFrame(self, frame, hour, mins, colour):
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
   
   def CreateWordTimeFrame(self, frame, hour, mins, colour, subMode):
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
            if mins == 45: mw = 3   #TO
            elif mins == 59: mw = 5 #MIN TO
            else: mw = 1            #MINS TO
         else:
            if mins == 15 or mins == 30: mw = 2  #PAST
            elif mins == 1: mw = 4                #MIN PAST
            else: mw = 0                         #MINS PAST
         for word in self.MIN_WORDS[mw]:
            frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #HOUR_NUM
      if (hour > 12): h = hour - 12
      else: h = hour
      for word in self.HOUR_NUM[h]:
         frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #TOD_WORDS
      if subMode == 1:
         if (hour < 12): tod = 2
         elif ( hour < 18): tod = 3
         elif ( hour < 21): tod = 4
         else: tod = 5
         for word in self.TOD_WORDS[tod]:
            frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
      
      #TOD_WORDS (AM/PM)
      if subMode == 2:
         if (hour < 12): tod = 0
         else: tod = 1
         for word in self.TOD_WORDS[tod]:
            frameLib.DrawFrameHLine(frame, word['x'], word['y'], word['len'], colour)
