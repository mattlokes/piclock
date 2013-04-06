################################################################
#                                                              #
#        Name: GridInterface_Sim                               #
#      Author: mattlokes                                       #
#                                                              #
# Description: Grid Interface simulator which offers a drop    #
#              in replacement for the actual IO interface to   #
#              the LED Grid matrix                             #
#                                                              #
################################################################

from GridGui import *

class GridInterface_Sim:
    def __init__(self, x_size, y_size, pad_size, conf_path):
        simgui = GridGui(x_size,y_size,pad_size,conf_path)
	simgui.run()
    
    #Set Pixel 
    def setpixel(self,x,y,rval,gval,bval):
        pass

    #Clear Pixel
    def clearpixel(self,x,y):
        pass

    #Draw Line
    def drawline(self,x0,x1,y0,y1,rval,gval,bval):
        pass

    #Draw Rectangle
    def drawrect(self,x0,y0,width,height,rval,gval,bval):
        pass

    #Draw Filled Rectangle
    def drawfilledrect(self,x0,y0,width,height,rval,gval,bval):
        pass

    #Clear Display
    def cleardisplay(self):
        pass

    #Get Light Value
    def getlightvalue(self):
        pass
