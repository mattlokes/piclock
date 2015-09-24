CFLAGS=-g -O0 -Wall -Wformat
LDFLAGS=-lm

all: bin/ledInterface


bin/ledInterface: ws2812_rpi.c ws2812_rpi.h main.c
	mkdir -p bin
	gcc ${CFLAGS} ${LDFLAGS} $+ -o $@
