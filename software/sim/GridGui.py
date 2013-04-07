################################################################
#                                                              #
#        Name: GridGui.py                                      #
#      Author: mattlokes                                       #
#                                                              #
# Description: Grid Interface simulator made from tkinter      #
#              widgets. Runs in its own thread with a queue    #
#              to make changes race free                       #
#                                                              #
################################################################


from Tkinter import *
import time
import copy
import threading
import random
import Queue

class GridGui(threading.Thread):
    
    grid_x = 0
    grid_y = 0
    grid_pad = 0
    grid_conf_path = ""
    grid = []
    cols = []
    rows = []
    e = []

    def __init__(self,master,queue,x_size,y_size,pad_size,conf_path):
        threading.Thread.__init__(self) #MagicT
	self.queue = queue        

        self.grid_x = x_size #16
        self.grid_y = y_size #14
        self.grid_pad = pad_size #3
        self.grid_conf_path = conf_path #"./grid.conf"
        self.start()
    
    def callback(self):
        self.root.quit()

    def run(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW",self.callback)
        #variables
        emp_line_count = 0

        #Read config file
        conf_f = open(self.grid_conf_path)
        conf_lines = conf_f.readlines()

        #Condition config array
        #  Strip Comments
	for i in range(len(conf_lines)):
	    if conf_lines[i].startswith('#'):
		conf_lines[i] = ''
	
	#  Strip End Lines
	for i in range(len(conf_lines)):
	    conf_lines[i] = conf_lines[i].rstrip('\n')

	#  Strip Empty Lines
	for i in range(len(conf_lines)):
	    if conf_lines[i] == '':
		emp_line_count = emp_line_count + 1

	#print emp_line_count

	for i in range(emp_line_count):
	    conf_lines.remove('')
		
	#Parse Lines into 2D letter array

	for i in range(len(conf_lines)):
	    conf_lines[i] = conf_lines[i].split(',')

	#complete a row at a time for the number of columns
	for i in range(self.grid_y+(2*self.grid_pad)):
	    self.cols = []
	    for j in range(self.grid_x+(2*self.grid_pad)):
		if j < self.grid_pad or \
		   j >= (self.grid_x+self.grid_pad) or \
		   i < self.grid_pad or \
		   i >= (self.grid_y+self.grid_pad):
		    self.e = Label(bg="black",fg="white", text="   ", font=("Arial",14))
		else:
		    self.e = Label(bg="black",fg="grey15", text=conf_lines[i-self.grid_pad][j-self.grid_pad]+"  ", font=("Arial",14))
		self.e.grid(row=i, column=j, sticky=NSEW)
		self.cols.append(self.e)
	    self.rows.append(self.cols)
        self.root.mainloop()
 
    def _processIncoming(self):
        while self.queue.qsize():
            try:
                msg = copy.deepcopy(self.queue.get(0))
                if msg["mtype"] == "sp":
                    #SET SINGLE LETTER
                    tmpx = msg["x"]+self.grid_pad
                    tmpy = msg["y"]+self.grid_pad
                    tmpcolor = '#%02x%02x%02x' % (msg["R"], msg["G"], msg["B"])
                    self.rows[tmpx][tmpy]["fg"] = tmpcolor
                    self.root.update()
                elif msg["mtype"] == "cp":
                    #RESET SINGLE LETTER
                    tmpx = msg["x"]+self.grid_pad
                    tmpy = msg["y"]+self.grid_pad
                    self.rows[tmpx][tmpy]["fg"] = "grey15"
                    self.root.update()
                elif msg["mtype"] == "dl":
                    #DRAW LINE OF LETTERS
		    # TODO
                    pass
                elif msg["mtype"] == "dr":
                    #DRAW RECTANGLE OF LETTERS
                    # TODO
                    pass
                elif msg["mtype"] == "dfr":
                    #DRAW FILLED RECTANGLES OF LETTERS
                    # TODO
                    pass
                elif msg["mtype"] == "cd":
                    #CLEAR ENTIRE DISPLAY
                    # TODO
                    pass
                elif msg["mtype"] == "glv":
                    #GET LIGHT VALUE
                    # TODO
                    pass
                else:
                    print "UNDEFINED MESSAGE TYPE"
            except Queue.Empty:
                print "emptyQ"

    def _periodicCall(self):
        self._processIncoming()
        self.root.after(50, self._periodicCall)

    def start_polling(self):
        self._periodicCall()
