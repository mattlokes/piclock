################################################################
#                                                              #
#        Name: GridInterface_Sim.py                            #
#      Author: mattlokes                                       #
#                                                              #
# Description: Grid Interface simulator which offers a drop    #
#              in replacement for the actual IO interface to   #
#              the LED Grid matrix                             #
#                                                              #
################################################################

from GridGui import *

class GridInterface_Sim:
    def __init__(self,x_size, y_size, pad_size, conf_path):
        self.queue = Queue.Queue()
        simgui = GridGui(0,self.queue,x_size,y_size,pad_size,conf_path)
        time.sleep(1)
        simgui.start_polling()
        
    #Set Pixel (sp)
    def setpixel(self,x,y,rval,gval,bval):
        msg = {'mtype':'sp','x':x, 'y':y,'R':rval,'G':gval,'B':bval}
        self.queue.put(msg)

    #Clear Pixel (cp)
    def clearpixel(self,x,y):
        msg = {'mtype':'cp','x':x, 'y':y}
        self.queue.put(msg)


    #Draw Line (dl)
    def drawline(self,x0,x1,y0,y1,rval,gval,bval):
        pass

    #Draw Rectangle (dr)
    def drawrect(self,x0,y0,width,height,rval,gval,bval):
        pass

    #Draw Filled Rectangle (dfr)
    def drawfilledrect(self,x0,y0,width,height,rval,gval,bval):
        pass

    #Clear Display (cd)
    def cleardisplay(self):
        msg = {'mtype':'cd'}
        self.queue.put(msg)
        pass

    #Get Light Value (glv)
    def getlightvalue(self):
        pass
