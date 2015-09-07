#!/usr/bin/python
import zmq
import sys
import time

context = zmq.Context()
print "Sending... {0}   down   {1}".format(sys.argv[2], sys.argv[1])
#
publisher = context.socket (zmq.PUB)
#publisher.bind("ipc:///tmp/cmdQ")
publisher.connect(sys.argv[1])
time.sleep(0.3)
publisher.send(sys.argv[2])

#import zmq
#from random import randrange
#
#context = zmq.Context()
#socket = context.socket(zmq.PUB)
#socket.bind("ipc:///tmp/cmdQ")
#
#while True:
#    zipcode = randrange(1, 100000)
#    temperature = randrange(-80, 135)
#
#    relhumidity = randrange(10, 60)
#
#    socket.send_string("%i %i %i" % (zipcode, temperature, relhumidity))
