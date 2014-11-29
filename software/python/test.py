import Queue
import clockApp
import time
import frameLib

rxCmd = Queue.Queue()
txCmd = Queue.Queue()
frame = Queue.Queue()

ca = clockApp.clockApp( frame, txCmd, rxCmd )
ca.startup()

while True:
   if not frame.empty():
      fr = frame.get()
      print "-- dst: {0} -- src: {1} --".format(fr['dst'], fr['src'])
      frameLib.debugFramePrint(fr['dat'])
   time.sleep(0.1)


