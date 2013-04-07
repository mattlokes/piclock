from GridInterface_Sim import *
from GridWordDef import *

def printdiagonal():
    for i in range(14):
        gis.setpixel(i,i,255,255,255)

def printclock():
    gwd = GridWordDef()
    #LOOP every 3 seconds
    #GET TIME
    #PARSE TIME
    #THE TIME IS
    #MINUTES
    #HOUR
    #MORNING,AFTERNOON, EVENING, NIGHT?
    pass
    

gis = GridInterface_Sim(16,14,3,'./grid.conf')
#printdiagonal()
printclock()
