import zmq
import sys
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



