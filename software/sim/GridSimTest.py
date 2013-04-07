from GridInterface_Sim import *

gis = GridInterface_Sim(16,14,3,'./grid.conf')
for i in range(14):
    gis.setpixel(i,i,255,255,255)
