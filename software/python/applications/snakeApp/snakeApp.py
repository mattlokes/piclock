#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#          Application Name:   Snake
#                    Author:   Matt
#
#               Description:   Snake Game! 
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import random

from framework.components.application import *

from libraries.frameLib import *
from libraries.systemLib import *

class snakeApp():
   
 
   ID = "SNAKE"
   appPollTime = 0.1    #10Hz
   rxPollTime = 0.02 #50Hz  
   
   forceUpdate = False

   snakeMode = "Normal"
   
   frame = []
   snakeColour = [0x00,0xFF,0x00]  #Green
   fruitColour = [0x00,0x00,0xFF]  #Red
   
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
            frameLib.DrawFramePixel(self.frame, tail[0], tail[1], [0x00,0x00,0x00])

         #Draw New Snake Head
         self.snakeBody.append(tmpHead)
         self.snakeHead = tmpHead
         frameLib.DrawFramePixel(self.frame, tmpHead[0], tmpHead[1], self.snakeColour)
      else:
         self.snakeClear()

      self.framePush(self.frame)
         
   def snakeClear(self):
      frameLib.CreateBlankFrame(self.frame)
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

   def framePush(self, frame):
      self.parent.txQueue.put({'dst': "DISP",
                               'src': self.ID,
                               'typ': "FRAME",
                               'dat': frame})
   
