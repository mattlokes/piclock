#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#   Application Name:   Colour Test App
#             Author:   Matt
#
#       Description:   Use for Color Calibration
#                      of the LED Grid.
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import signal
import sys
from zmq.eventloop import ioloop
from libraries.application import *
from libraries.frameLib import *
from libraries.systemLib import *

class colourTestApp():
   
   ID = "COLOUR"
   appPollTime = 0.035    #10Hz
   
   forceUpdate = False

   #colourTestMode = "colour"
   colourTestMode = "vLineAni"

   frame = bytearray(1024)
   frameColour = frameLib.GREEN
   tickCount = 0
  
   def __init__(self, parent, **kwargs):
      self.parent = parent

   def startup(self):
      self.forceUpdate = True

   def incomingRx(self, cmd):
      # Decode Incoming Cmd Packets
      # Colour Change Command
      if cmd['typ'] == "COLOR":
         self.frameColour = bytearray( [0x00,
                                       int(cmd['dat'][4:6],16),  #R
                                       int(cmd['dat'][2:4],16),  #G
                                       int(cmd['dat'][0:2],16)]) #B 
         self.forceUpdate = True
         
      # Time Format Change
      if cmd['typ'] == "MODE":
         self.forceUpdate = True

   # Main Application Loop
   def appTick(self):
      if   self.colourTestMode == "vLineAni":
           self.generateVertLineAnimation()
      elif self.colourTestMode == "colour":
         if self.forceUpdate:
            self.frame = bytearray(1024)
            frameLib.CreateColourFrame( self.frame, self.frameColour )
            self.parent.framePush("DISP",self.frame)
            self.forceUpdate = False
   
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
         self.parent.framePush("DISP",self.frame)
         
         if self.tickCount >= animationDelay + 256:
            self.frame = bytearray(1024)
            self.tickCount = 0

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
    app = application( colourTestApp , "ipc:///tmp/cmdQRx", "ipc:///tmp/cmdQTx" , "ipc:///tmp/frameQ")
    signal.signal(signal.SIGINT, app.extkill)
    app.startup()
    ioloop.IOLoop.instance().start()
