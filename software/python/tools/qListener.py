#!/usr/bin/python
import zmq
import sys
import signal

def sigint_hand(signal,frame):
   sys.exit(0)

signal.signal( signal.SIGINT, sigint_hand)

context = zmq.Context()
print "Listening on {0} .....".format(sys.argv[1])
#
subscriber = context.socket (zmq.SUB)
subscriber.connect (sys.argv[1])
subscriber.setsockopt(zmq.SUBSCRIBE, '')
#
while True:
    message = subscriber.recv()
    print "{0} : [{1}]".format(message, len(message))



