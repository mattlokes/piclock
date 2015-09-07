#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#       
#                      File:   frameLib.py
#                    Author:   Matt
#
#               Description:   A Group of functions useful for frame creation and modification 
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import sys

class frameLib ():
   BLANK   =bytearray([0x00,0x00,0x00,0x00])
   RED     =bytearray([0x00,0xFF,0x00,0x00])
   GREEN   =bytearray([0x00,0x00,0xFF,0x00])
   BLUE    =bytearray([0x00,0x00,0x00,0xFF])
   CYAN    =bytearray([0x00,0x00,0xFF,0xFF])
   YELLOW  =bytearray([0x00,0xFF,0xFF,0x00])
   MAGENTA =bytearray([0x00,0xFF,0x00,0xFF])
   WHITE   =bytearray([0x00,0xFF,0xFF,0xFF])
   
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
   
   @staticmethod 
   def CreateBlankFrame ( frame ):
      frame = bytearray(256*4)
      #for i in range(0, 256*4):
      #    frame[i] = 0
   
   @staticmethod 
   def CreateColourFrame (frame, colour):
      for i in range(0,256):
         p = (4*i)
         frame[p:p+4] = colour
   
   @staticmethod 
   def DrawFramePixel ( frame, x , y, colour):
      if len(frame) != 256*4:
         print "SFP - INVALID FRAME len(frame) = {0}".format(len(frame))
      else:
         if x < 16 and y < 16: 
            p = (4*y*16)+(4*x)
            frame[p:p+4] = colour
         else:
            pass #Silently Ignore
   
   @staticmethod 
   def DrawFrameHLine ( frame, x, y, ln , colour):
      if len(frame) != 256*4:
         print "SFP - INVALID FRAME len(frame) = {0}".format(len(frame))
      else:
         for i in range(0,ln):
            p = (4*y*16)+(4*(x+i))
            #print "frame[{0}:{1}] @ len {2}".format(p,p+4,len(frame))
            frame[p:p+4] = colour
   
   @staticmethod 
   def GetFramePixel ( frame, x , y):
      if len(frame) != 256*4:
         print "SFP - INVALID FRAME len(frame) = {0}".format(len(frame))
      else:
         if x < 16 and y < 16: 
           p = (4*y*16)+(4*x)
           return frame[p:p+4]
         else:
            pass #Silently Ignore

   @staticmethod
   def ShiftFrameLeft (frame ,shiftnum):
      for i in range(0,shiftnum):
         for i in range(0,4):frame.pop(0)       #Remove 4 Bytes
         for i in range(0,4):frame.append(0x00) #Add 4 Bytes
         for r in range(0,16):
            p = ((4*16*r)+(4*15))
            frame[p:p+4] = bytearray([0x00,0x00,0x00,0x00]) 
   
   @staticmethod
   def ShiftFrameRight (frame ,shiftnum):
      for i in range(0,shiftnum):
         frame.insert(0,[0x00,0x00,0x00])
         frame.pop(256)
         for r in range(0,16):
            frame[(16*r)] = [0x00,0x00,0x00]
   
   @staticmethod
   def ShiftFrameUp (frame ,shiftnum):
      for i in range(0,shiftnum):
         for r in range(0,16): 
            frame.pop(0)
            frame.append([0x00,0x00,0x00])
   
   @staticmethod
   def ShiftFrameDown (frame ,shiftnum):
      for i in range(0,shiftnum):
         for r in range(0,16): 
            frame.insert(0,[0x00,0x00,0x00])
            frame.pop(256)

   @staticmethod 
   def CreateEqualizerFrame( frame , aChans) :
      if len(aChans) != 16:
         print "CEF - INVALID aChans Length "+ str(len(aChans))
      else:
         for i in range (0,16):
            frameLib.DrawFramePixel( frame, i, 15-aChans[i],frameLib.CYAN)
   
   @staticmethod 
   def CreateEqualizer2Frame( frame , aChans) :
      if len(aChans) != 16:
         print "CEF - INVALID aChans Length "+ str(len(aChans))
      else:
         for i in range (0,16):
            for j in range(0,aChans[i]):
               if j < 6:
                  frameLib.DrawFramePixel( frame, i, 15-j,frameLib.GREEN)
               elif j < 12:
                  frameLib.DrawFramePixel( frame, i, 15-j,frameLib.YELLOW)
               else:
                  frameLib.DrawFramePixel( frame, i, 15-j,frameLib.RED)
   @staticmethod 
   def debugFramePrint ( frame ):
      if len(frame) != 256*4:
         print "DFP - INVALID FRAME"
      else:
         for i in range(0,16): #x
            for j in range(0,16):#y
               p = (4*i*16)+(4*j)
               if frame[p:p+4] == frameLib.BLANK:
                  sys.stdout.write(' ')
               elif frame[p:p+4] == frameLib.RED:
                  sys.stdout.write('R')
               elif frame[p:p+4] == frameLib.GREEN:
                  sys.stdout.write('G')
               elif frame[p:p+4] == frameLib.BLUE:
                  sys.stdout.write('B')
               elif frame[p:p+4] == frameLib.CYAN:
                  sys.stdout.write('C')
               elif frame[p:p+4] == frameLib.YELLOW:
                  sys.stdout.write('Y')
               elif frame[p:p+4] == frameLib.MAGENTA:
                  sys.stdout.write('M')
               elif frame[p:p+4] == frameLib.WHITE:
                  sys.stdout.write('W')
               elif frame[p:p+4] != frameLib.BLANK:
                  sys.stdout.write('O')
               sys.stdout.write(' ')
            sys.stdout.write('\n')
   
   @staticmethod 
   def debugFrameLetterPrint ( frame ):
      if len(frame) != 256*4:
         print "DFP - INVALID FRAME"
      else:
         print " --------------------------------- "
         for i in range(0,16): #x
            sys.stdout.write('| ')
            for j in range(0,16):#y
               p = (4*i*16)+(4*j)
               if frame[p:p+4] == frameLib.BLANK:
                  sys.stdout.write(' ')
               elif frame[p:p+4] != frameLib.BLANK:
                  sys.stdout.write(frameLib.LETTERGRID[(i*16)+j])
               sys.stdout.write(' ')
            sys.stdout.write('|\n')
         print " --------------------------------- "
