#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#       
#                      File:   frameLib.py
#                    Author:   Matt
#
#               Description:   A Group of functions useful for frame creation and modification 
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import sys

BLANK=[0x00,0x00,0x00]
RED=[0x00,0x00,0xFF]
GREEN=[0x00,0xFF,0x00]
BLUE=[0xFF,0x00,0x00]
CYAN=[0xFF,0xFF,0x00]
YELLOW=[0x00,0xFF,0xFF]
MAGENTA=[0xFF,0x00,0xFF]
WHITE=[0xFF,0xFF,0xFF]

def CreateBlankFrame ( frame ):
   frame[:] = []
   for i in range(0,256):
      frame.append([0x00,0x00,0x00])

def DrawFramePixel ( frame, x , y, colour):
   if len(frame) != 256:
      print "SFP - INVALID FRAME"
   else:
      frame[(y*16)+x] = colour

def DrawFrameHLine ( frame, x, y, ln , colour):
   if len(frame) != 256:
      print "SFP - INVALID FRAME"
   else:
      for i in range(0,ln):
         frame[(y*16)+(x+i)] = colour

def CreateEqualizerFrame( frame , aChans) :
   if len(aChans) != 16:
      print "CEF - INVALID aChans Length "+ str(len(aChans))
   else:
      for i in range (0,16):
         DrawFramePixel( frame, i, 15-aChans[i],CYAN)

def CreateEqualizer2Frame( frame , aChans) :
   if len(aChans) != 16:
      print "CEF - INVALID aChans Length "+ str(len(aChans))
   else:
      for i in range (0,16):
         for j in range(0,aChans[i]):
            if j < 6:
               DrawFramePixel( frame, i, 15-j,GREEN)
            elif j < 12:
               DrawFramePixel( frame, i, 15-j,YELLOW)
            else:
               DrawFramePixel( frame, i, 15-j,RED)

def debugFramePrint ( frame ):
   if len(frame) != 256:
      print "DFP - INVALID FRAME"
   else:
      for i in range(0,16): #x
         for j in range(0,16):#y
            if frame[(i*16)+j] == BLANK:
               sys.stdout.write(' ')
            elif frame[(i*16)+j] == RED:
               sys.stdout.write('R')
            elif frame[(i*16)+j] == GREEN:
               sys.stdout.write('G')
            elif frame[(i*16)+j] == BLUE:
               sys.stdout.write('B')
            elif frame[(i*16)+j] == CYAN:
               sys.stdout.write('C')
            elif frame[(i*16)+j] == YELLOW:
               sys.stdout.write('Y')
            elif frame[(i*16)+j] == MAGENTA:
               sys.stdout.write('M')
            elif frame[(i*16)+j] == WHITE:
               sys.stdout.write('W')
            sys.stdout.write(' ')
         sys.stdout.write('\n')
