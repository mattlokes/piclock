import Queue
import time
import frameLib

import hwInterface

import clockApp

rxCmd = Queue.Queue()
txCmd = Queue.Queue()
frame = Queue.Queue()

hw = hwInterface.hwInterface ( frame, txCmd, rxCmd )
hw.startup()

ca = clockApp.clockApp( frame, txCmd, rxCmd )
ca.startup()

while True:
   time.sleep(5)


