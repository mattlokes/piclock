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
        timestr = datetime.datetime.now().strftime('%I%M%p') #'HHMM(PM/AM)'
        #timestr = '1212PM' #debug timestr
        if oldtimestr != timestr:
            gis.cleardisplay()
        #print timestr[4:6]
        #THE TIME IS
        printarray(gwd.the_time_is)
        printarray(gwd.time_conv(timestr))
        #MORNING,AFTERNOON, EVENING, NIGHT?
        #IN THE MORNING - 12:01AM -> 12:01PM
        if timestr[4:6] == 'AM':
            printarray(gwd.in_the+gwd.morning)
        #In THE AFTERNOON - 12:01PM-6:00Pm
        elif (int(timestr[0:2]) == 12 and timestr[4:6] == 'PM') or \
           (int(timestr[0:2]) >= 1 and int(timestr[0:2]) <= 5 and timestr[4:6] == 'PM'):
            printarray(gwd.in_the+gwd.afternoon)
        #IN THE EVENING   - 6:00PM -> 9:00PM
        elif (int(timestr[0:2]) >= 6 and int(timestr[0:2]) <= 8 and timestr[4:6] == 'PM'):
            printarray(gwd.in_the+gwd.evening)
        #AT NIGHT         - 9:00PM -> 12:00PM
        elif (int(timestr[0:2]) >= 9 and timestr[4:6] == 'PM'):
            printarray(gwd.at+gwd.night)
        
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
