#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#   Application Name:   Colour Test App
#             Author:   Matt
#
#       Description:   Use for Color Calibration
#                      of the LED Grid.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import Queue
import threading
import time
import datetime

from libraries.frameLib import *

class colourTestApp(threading.Thread):
   
   ID = "COLOUR"
   dying = False
   appPollTime = 0.02    #10Hz
   rxCmdPollTime = 0.02 #50Hz  
   forceUpdate = False

   #colourTestMode = "colour"
   colourTestMode = "vLineAni"

   frame = []
   frameColour = frameLib.GREEN
   tickCount = 0
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
      print "Stopping {0} Application...".format(self.ID)

   def __rxCmdPoll(self):
      cmd = self.rxCmdQueue.get()
      # Decode Incoming Cmd Packets
      #print "-- {0} -- {1} --".format(cmd['typ'],cmd['dat'])
      # Colour Change Command
      if cmd['typ'] == "COLOR":
         self.frameColour = [int(cmd['dat'][4:6],16), #R
                             int(cmd['dat'][2:4],16), #G
                             int(cmd['dat'][0:2],16)] #B
         self.forceUpdate = True
      # Time Format Change
      elif cmd['typ'] == "MODE":
         self.forceUpdate = True

      if not self.dying: threading.Timer(self.rxCmdPollTime, self.__rxCmdPoll).start() #rxCmdQueue Poller

   # Main Application Loop
   def __appPoll(self):
      if   self.colourTestMode == "vLineAni":
         self.__generateVertLineAnimation()
      elif self.colourTestMode == "colour":
         if self.forceUpdate:
            frameLib.CreateBlankFrame(self.frame)
            frameLib.CreateColourFrame( self.frame, self.frameColour )
            self.__framePush(self.frame)
            self.forceUpdate = False
      
      if not self.dying: threading.Timer(self.appPollTime, self.__appPoll).start() #App Poller
   
   def __framePush(self, frame):
      self.txCmdQueue.put({'dst': "DISP",
                           'src': self.ID,
                           'typ': "frame",
                           'dat': frame})

   def __generateVertLineAnimation( self ):
      animationDelay = 20
      self.tickCount += 1
      if self.tickCount >= animationDelay:
         tickBase = self.tickCount - animationDelay
         tickX = tickBase / 16
         tickY = tickBase % 16
         colPtr = tickX % 3
         dirPtr = tickX % 2
        
         if dirPtr == 1: tickY = 15 - tickY

         if colPtr == 0:
            frameLib.DrawFramePixel(self.frame, tickX, tickY, frameLib.RED)
         elif colPtr == 1:
            frameLib.DrawFramePixel(self.frame, tickX, tickY, frameLib.GREEN)
         elif colPtr == 2:
            frameLib.DrawFramePixel(self.frame, tickX, tickY, frameLib.BLUE)
         self.__framePush(self.frame)
         
         if self.tickCount >= animationDelay + 256:
            frameLib.CreateBlankFrame( self.frame )
            self.tickCount = 0
   
