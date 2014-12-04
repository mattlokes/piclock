import Queue
import clockApp
import wsInterface
import time
import frameLib

rxCmd = Queue.Queue()
txCmd = Queue.Queue()
frame = Queue.Queue()

ca = clockApp.clockApp( frame, txCmd, rxCmd )
ca.startup()

ws = wsInterface.wsInterface( rxCmd )
ws.startup()
