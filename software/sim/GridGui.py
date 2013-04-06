from Tkinter import *

#Parameters
grid_x = 16
grid_y = 14
grid_pad = 3
grid_conf_path = "./grid.conf"

#variables
emp_line_count = 0

#Read config file
conf_f = open(grid_conf_path)
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

#print conf_lines
 


rows = []
#complete a row at a time for the number of columns
for i in range(grid_y+(2*grid_pad)):
    cols = []
    for j in range(grid_x+(2*grid_pad)):
	if j < grid_pad or \
           j >= (grid_x+grid_pad) or \
           i < grid_pad or \
           i >= (grid_y+grid_pad):
	    #e = Label(bg="black",fg="white", text="."+str(i)+str(j)+" ", font=("Arial",14))
	    e = Label(bg="black",fg="white", text="   ", font=("Arial",14))
        else:
            #e = Label(bg="black",fg="white", text="T"+str(i)+str(j)+" ", font=("Arial",14))
            e = Label(bg="black",fg="grey15", text=conf_lines[i-grid_pad][j-grid_pad]+"  ", font=("Arial",14))
        e.grid(row=i, column=j, sticky=NSEW)
        cols.append(e)
    rows.append(cols)

#def onPress():
#    for row in rows:
#        for col in row:
#            print col.get(),
#        print
#Button(text='Fetch', command=onPress).grid()
mainloop()
