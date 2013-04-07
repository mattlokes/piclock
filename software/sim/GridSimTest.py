from GridInterface_Sim import *
from GridWordDef import *
import datetime

def printdiagonal():
    for i in range(14):
        gis.setpixel(i,i,255,255,255)

def printclock():
    gwd = GridWordDef()
    oldtimestr = ""
    while 1 :
        #GET TIME
        #timestr = datetime.datetime.now().strftime('%I%M%p') #'HHMM(PM/AM)'
        timestr = '0100Pm' #debug timestr
        if oldtimestr != timestr:
            gis.cleardisplay()
        #print timestr[4:6]
        #THE TIME IS
        printarray(gwd.the_time_is)
        printarray(gwd.time_conv(timestr))
        #MORNING,AFTERNOON, EVENING, NIGHT?
        
        oldtimestr = timestr
        time.sleep(3)
        
    

def printtestwords():
    gwd = GridWordDef()
    for it in gwd.iterator:
        printarray(it)
        time.sleep(0.5)
        gis.cleardisplay()
        time.sleep(0.5)

def printarray(pixel_array):
    for pixel in pixel_array:
        gis.setpixel(pixel[1],pixel[0],255,255,255)
    

gis = GridInterface_Sim(16,14,3,'./grid.conf')
#printdiagonal()
printclock()
#printtestwords()
