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

LETTERGRID = [ 'Q','T','H','E','R','V','I','T','I','M','E','O','P','I','S','N', 
               'T','W','E','N','T','Y','U','T','E','N','A','F','I','V','E','U', 
               'E','I','G','H','T','P','F','O','U','R','K','U','T','W','O','Y', 
               'A','T','H','R','E','E','Z','O','N','E','W','S','E','V','E','N', 
               'L','Q','U','A','R','T','E','R','E','M','N','I','N','E','N','O', 
               'S','I','X','T','W','E','L','V','E','A','E','L','E','V','E','N', 
               'I','T','H','I','R','T','E','E','N','T','H','A','L','F','S','R', 
               'V','E','M','I','N','U','T','E','S','T','S','P','A','S','T','I', 
               'F','T','O','Y','O','N','E','V','E','T','W','E','L','V','E','M', 
               'T','H','R','E','E','L','C','S','E','V','E','N','I','N','E','Y', 
               'K','L','S','I','X','B','T','W','O','F','G','F','O','U','R','W', 
               'I','E','I','G','H','T','R','Z','E','L','E','V','E','N','S','V', 
               'N','A','F','I','V','E','C','O','E','T','E','N','Q','A','M','F', 
               'Y','I','N','B','A','T','H','E','R','E','V','E','N','I','N','G', 
               'P','M','T','A','F','T','E','R','N','O','O','N','W','V','C','E', 
               'M','O','R','N','I','N','G','U','M','I','D','N','I','G','H','T']

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
            elif frame[(i*16)+j] != BLANK:
               sys.stdout.write('O')
            sys.stdout.write(' ')
         sys.stdout.write('\n')

def debugFrameLetterPrint ( frame ):
   if len(frame) != 256:
      print "DFP - INVALID FRAME"
   else:
      print "-----------------------------------"
      for i in range(0,16): #x
         sys.stdout.write('| ')
         for j in range(0,16):#y
            if frame[(i*16)+j] == BLANK:
               sys.stdout.write(' ')
            elif frame[(i*16)+j] != BLANK:
               sys.stdout.write(LETTERGRID[(i*16)+j])
            sys.stdout.write(' ')
         sys.stdout.write('|\n')
      print "-----------------------------------"
