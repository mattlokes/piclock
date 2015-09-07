#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#          Application Name:   Snake
#                    Author:   Matt
#
#               Description:   Snake Game! 
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import signal
import sys
from zmq.eventloop import ioloop
from libraries.application import *

from libraries.frameLib import *
from libraries.systemLib import *

import random

class snakeApp():
   
 
   ID = "SNAKE"
   appPollTime = 0.1    #10Hz
   
   forceUpdate = False

   snakeMode = "Normal"
   
   frame = bytearray(1024)
   snakeColour = bytearray([0x00,0xFF,0x00,0x00])  #Green
   fruitColour = bytearray([0x00,0x00,0xFF,0x00])  #Red
   
   score = 0

   snakeBody   = []
   snakeHead   = []
   snakeDir    = "RIGHT"
   snakeNxtDir = None

   fruit       = [3,3]

   def __init__(self, parent, **kwargs):
      self.parent = parent

   def startup(self):
      self.snakeClear()
      self.forceUpdate = True
   

   def incomingRx ( self, cmd ):
      # Decode Incoming Cmd Packets
      # Colour Change Command
      if cmd['typ'] == "DIR":
         self.snakeNxtDir = cmd['dat']
      

   # Main Application Loop
   def appTick(self):
      #Change Direction
      if self.snakeNxtDir != None:
         if (self.snakeDir == "RIGHT" and self.snakeNxtDir == "LEFT") or \
            (self.snakeDir == "UP" and self.snakeNxtDir == "DOWN") or \
            (self.snakeDir == "DOWN" and self.snakeNxtDir == "UP") or \
            (self.snakeDir == "LEFT" and self.snakeNxtDir == "RIGHT"):
            pass #Ignore Change
         elif self.snakeNxtDir == "ENTER":
            pass #TODO PAUSE GAME NOT APP!
         else:
            self.snakeDir = self.snakeNxtDir

      #Calculate Next Move
      if self.snakeDir == "RIGHT":  tmpHead = [self.snakeHead[0]+1, self.snakeHead[1]]
      elif self.snakeDir == "LEFT": tmpHead = [self.snakeHead[0]-1, self.snakeHead[1]]
      elif self.snakeDir == "UP":   tmpHead = [self.snakeHead[0],   self.snakeHead[1]-1]
      elif self.snakeDir == "DOWN": tmpHead = [self.snakeHead[0],   self.snakeHead[1]+1]

      #Check for Wrapping
      if tmpHead[0] > 15: tmpHead[0] = 0
      if tmpHead[0] < 0:  tmpHead[0] = 15
      if tmpHead[1] > 15: tmpHead[1] = 0
      if tmpHead[1] < 0:  tmpHead[1] = 15

      #Check for Fruit / Self Collision
      if frameLib.GetFramePixel(self.frame, tmpHead[0], tmpHead[1]) != self.snakeColour: #Not Self Collision
         if tmpHead == self.fruit: #Fruit Collision
            self.score += 1
            #No Snake Pop
            self.fruit = self.snakeGenFruit()
            frameLib.DrawFramePixel(self.frame, self.fruit[0], self.fruit[1], self.fruitColour)
         else:
            #Remove Tail
            tail = self.snakeBody.pop(0)
            frameLib.DrawFramePixel(self.frame, tail[0], tail[1], bytearray([0x00,0x00,0x00,0x00]))

         #Draw New Snake Head
         self.snakeBody.append(tmpHead)
         self.snakeHead = tmpHead
         frameLib.DrawFramePixel(self.frame, tmpHead[0], tmpHead[1], self.snakeColour)
      else:
         self.snakeClear()

      self.parent.framePush("DISP",self.frame)
         
   def snakeClear(self):
      self.frame = bytearray(1024)
      self.score = 0
      self.snakeBody   = [[0,1],[1,1]]
      self.snakeHead   = [1,1]
      self.snakeDir    = "RIGHT"
      
      #Draw Init Snake
      for seg in self.snakeBody:
         frameLib.DrawFramePixel(self.frame, seg[0], seg[1], self.snakeColour)
     
      #Gen Fruit 
      self.fruit = self.snakeGenFruit()
      frameLib.DrawFramePixel(self.frame, self.fruit[0], self.fruit[1], self.fruitColour)

   def snakeGenFruit(self):
     validFruit = False
     while  not validFruit:
        tmpFruit = [random.randint(0,15), random.randint(0,15)]
        potPlace = frameLib.GetFramePixel(self.frame, tmpFruit[0], tmpFruit[1])
        validFruit = potPlace != self.snakeColour and potPlace != self.fruitColour
     return tmpFruit

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
    app = application( snakeApp , "ipc:///tmp/cmdQRx", "ipc:///tmp/cmdQTx" , "ipc:///tmp/frameQ")
    signal.signal(signal.SIGINT, app.extkill)
    app.startup()
    ioloop.IOLoop.instance().start()

