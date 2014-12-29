#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#   Application Name:   Colour Test App
#             Author:   Matt
#
#       Description:   Use for Color Calibration
#                      of the LED Grid.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

from libraries.frameLib import *
from libraries.systemLib import *

class colourTestApp():
   
   ID = "COLOUR"
   appPollTime = 0.02    #10Hz
   rxPollTime = 0.02 #50Hz  
   
   forceUpdate = False

   #colourTestMode = "colour"
   colourTestMode = "vLineAni"

   frame = []
   frameColour = frameLib.GREEN
   tickCount = 0
  
   def __init__(self, parent, **kwargs):
      self.parent = parent

   def startup(self):
      frameLib.CreateBlankFrame(self.frame)
      self.forceUpdate = True

   def incomingRx(self, cmd):
      # Decode Incoming Cmd Packets
      # Colour Change Command
      if cmd['typ'] == "COLOR":
         self.frameColour = [int(cmd['dat'][4:6],16), #R
                             int(cmd['dat'][2:4],16), #G
                             int(cmd['dat'][0:2],16)] #B
         self.forceUpdate = True
         
      # Time Format Change
      if cmd['typ'] == "MODE":
         self.forceUpdate = True
       
      if cmd['typ'] == "KILL":
         self.parent.kill()

   # Main Application Loop
   def appTick(self):
      if   self.colourTestMode == "vLineAni":
           self.generateVertLineAnimation()
      elif self.colourTestMode == "colour":
         if self.forceUpdate:
            frameLib.CreateBlankFrame(self.frame)
            frameLib.CreateColourFrame( self.frame, self.frameColour )
            self.framePush(self.frame)
            self.forceUpdate = False
   
   def framePush(self, frame):
      self.parent.txQueue.put({'dst': "DISP",
                               'src': self.ID,
                               'typ': "FRAME",
                               'dat': frame})

   def generateVertLineAnimation( self ):
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
         self.framePush(self.frame)
         
         if self.tickCount >= animationDelay + 256:
            frameLib.CreateBlankFrame( self.frame )
            self.tickCount = 0
   
