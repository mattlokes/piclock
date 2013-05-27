TEMPLATEROOT = ..

# compilation flags for gdb

CFLAGS  = -O1 -g
#CFLAGS  = -O1
ASFLAGS = -g 
#ASFLAGS =  
LIBS = spi.o stm32f10x_gpio.o stm32f10x_spi.o stm32f10x_rcc.o stm32f10x_tim.o

# object files

OBJS=  $(STARTUP) $(LIBS) main.o

# include common make file

include $(TEMPLATEROOT)/Makefile.common


