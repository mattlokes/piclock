CFLAGS=-g -O0 -Wall -Wformat
LDFLAGS=-lm
ZMQFLAGS=-I/usr/local/include  -L/usr/local/lib -lzmq

all: bin/ledDisplay


bin/ledDisplay: ws2812_rpi.c ws2812_rpi.h main.c
	mkdir -p bin
	gcc ${CFLAGS} ${LDFLAGS} ${ZMQFLAGS} $+ -o $@
