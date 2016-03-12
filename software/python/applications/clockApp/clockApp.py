#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#          Application Name:   Clock
#                    Author:   Matt
#
#               Description:   Clock Application using the basic functionality 
#                              of the LED Grid.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import signal
import sys
from zmq.eventloop import ioloop
from libraries.application import *
from libraries.frameLib import *
from libraries.systemLib import *

import datetime
import copy


class clockApp():
   
   #Import Constants for Fonts and Words
   from clockAppConsts import *  
 
   ID = "CLOCK"
   appPollTime = 0.05    #10Hz
   
   forceUpdate = False
   forceTran = False

   tranMode = "NONE"
   clockMode = "WORD"
   todMode = 0
   
   frame = bytearray(1024)
   oldFrame = bytearray(1024)
   tranBuffer = []

   timeColour = bytearray([0x00,0x51,0x00,0xFF])  #Default Colour
   timeHistory=""

   def __init__(self, parent, **kwargs):
      self.parent = parent

   def startup(self):
      self.forceUpdate = True

   def variableState(self):
      vState = []
      vState.append( {'name': "MODE", 'val': self.clockMode} )
      vState.append( {'name': "TRAN", 'val': self.tranMode} )

      if   self.todMode == 1: tod = "SUFFIX"
      elif self.todMode == 2: tod = "AMPM"
      else                  : tod = "NONE"
      vState.append( {'name': "TOD", 'val': tod} )

      colourStr = ''.join('{:02x}'.format(x) for x in self.timeColour)[2:] 
      vState.append( {'name': "COLOR", 'val': colourStr} )

      return vState

   def incomingRx ( self, cmd ):
      # Decode Incoming Cmd Packets
      # Colour Change Command
      if cmd['typ'] == "COLOR":
         self.timeColour = bytearray([0x00,
                                      int(cmd['dat'][0:2],16), #R
                                      int(cmd['dat'][2:4],16), #G
                                      int(cmd['dat'][4:6],16)] #B
                                    )
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

      if cmd['typ'] == "TRAN":
         self.tranMode = cmd['dat']
         self.forceTran = True

   # Main Application Loop
   def appTick(self):
      #Update Time
      get_h = datetime.datetime.now().time().hour
      get_m = datetime.datetime.now().time().minute
      timeHistoryCompare=str(get_h)+str(get_m)

      if self.timeHistory != timeHistoryCompare or self.forceUpdate or self.forceTran:
         self.oldFrame = copy.deepcopy(self.frame)
         self.frame = bytearray(1024) 
         self.CreateTimeFrame(self.frame, get_h, get_m, self.clockMode, self.timeColour )

         if not self.forceUpdate: self.CreateTimeFrameTransition( self.oldFrame, self.frame, self.tranMode, self.tranBuffer )
         else: self.tranBuffer.append( self.frame )

         self.timeHistory=timeHistoryCompare
         self.forceUpdate = False
         self.forceTran = False
 
      if len(self.tranBuffer) > 0:
         self.parent.framePush("DISP",self.tranBuffer.pop(0))
   
   def CreateTimeFrameTransition( self, oframe, nframe, tranMode, tranBuffer):
      if tranMode == "NONE":
         tranBuffer.append(nframe)
      if tranMode == "HSLIDE":
         for i in range(1,16):
            frameLib.ShiftFrameLeft(oframe, 1)
            tranBuffer.append(copy.deepcopy(oframe))
         for i in range(1,16):
            tmp = copy.deepcopy(nframe)
            frameLib.ShiftFrameRight(tmp, 16-i)
            tranBuffer.append(tmp)
         tranBuffer.append(nframe)
      if tranMode == "VSLIDE":
         for i in range(1,16):
            frameLib.ShiftFrameUp(oframe, 1)
            tranBuffer.append(copy.deepcopy(oframe))
         for i in range(1,16):
            tmp = copy.deepcopy(nframe)
            frameLib.ShiftFrameDown(tmp, 16-i)
            tranBuffer.append(tmp)
         tranBuffer.append(nframe)
     
      if tranMode == "FADE":
         speed = 20
         step = 1.0/speed
         
         for i in range(0,speed):
            tmp = copy.deepcopy(oframe)
            frameLib.DimLinearFrame(tmp, (speed-i)*step )
            tranBuffer.append(tmp)

         for i in range(0,12): tranBuffer.append(bytearray(1024))
 
         for i in range(0,speed):
            tmp = copy.deepcopy(nframe)
            frameLib.DimLinearFrame(tmp, i*step )
            tranBuffer.append(tmp)


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
    app = application( clockApp , cmdQRx, cmdQTx , frameQ, default=True)
    signal.signal(signal.SIGINT, app.extkill)
    app.startup()
    ioloop.IOLoop.instance().start()
