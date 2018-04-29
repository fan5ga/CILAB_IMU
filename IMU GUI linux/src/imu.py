#!/usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import serial

from multiprocessing import Process, Queue, freeze_support

import pylab
import os
import time

from tkinter import ttk
from time import sleep

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

from matplotlib import style

import tkFont

q1 = Queue()
q2 = Queue()
com = Queue()

com_flag = False
ax = ay = az = 0.0
yaw_mode = False
data_number = 0

axs = [0 for i in range(100)]
ays = [0 for i in range(100)]
azs = [0 for i in range(100)]
bxs = [0 for i in range(100)]
bys = [0 for i in range(100)]
bzs = [0 for i in range(100)]
cxs = [0 for i in range(100)]
cys = [0 for i in range(100)]
czs = [0 for i in range(100)]
ns = [i for i in range(100)]


style.use('fivethirtyeight')

fig = pylab.figure(figsize=[15, 15], dpi=50, facecolor='silver')

#ax = fig.gca()


# figures
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)
ax1.set_xlabel('Oritation')
ax2.set_xlabel('Acceleration')
ax3.set_xlabel('Magnetic')


data_a = 0

    
def animate2(q2):
    #global  axes, fig, axs,ays,azs,bxs,bys,bzs,cxs,cys,czs,
    if q2.empty():
        #sleep(0.05)
        return
    tmp = q2.get()
    x = q2.qsize()
    for i in range(x-1):
        q2.get()
    
    axs.append(tmp[0])
    axs.pop(0)
    ays.append(tmp[1])
    ays.pop(0)
    azs.append(tmp[2])
    azs.pop(0)

    bxs.append(tmp[3])
    bxs.pop(0)
    bys.append(tmp[4])
    bys.pop(0)
    bzs.append(tmp[5])
    bzs.pop(0)

    cxs.append(tmp[6])
    cxs.pop(0)
    cys.append(tmp[7])
    cys.pop(0)
    czs.append(tmp[8])
    czs.pop(0)


    ax1.clear()
    ax2.clear()
    ax3.clear()

    ax1.plot(ns, axs,color='r',label='X')
    ax1.plot(ns, ays,color='g',label='Y')
    ax1.plot(ns, azs,color='b',label='Z')

    ax2.plot(ns, bxs,color='r',label='X')
    ax2.plot(ns, bys,color='g',label='Y')
    ax2.plot(ns, bzs,color='b',label='Z')

    ax3.plot(ns, cxs,color='r',label='X')
    ax3.plot(ns, cys,color='g',label='Y')
    ax3.plot(ns, czs,color='b',label='Z')
    ax1.set_xlabel('Oritation')
    ax2.set_xlabel('Acceleration')
    ax3.set_xlabel('Magnetic')

    



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable(GL_TEXTURE_2D)

def drawText(position, textString):     
    font = pygame.font.SysFont ("Courier", 18, True)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))     
    textData = pygame.image.tostring(textSurface, "RGBA", True)     
    glRasterPos3d(*position)     
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def load_texture():
    textures = glGenTextures(6)

    for i in range(6):
        glBindTexture(GL_TEXTURE_2D, textures[i])
        #glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
        tmp = pygame.image.load(str(i+1)+'.png')
        img = pygame.image.tostring(tmp, "RGBA", 1)
        w, h = tmp.get_size()
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img )
        glGenerateMipmap(GL_TEXTURE_2D)
    return textures


def draw(textures, q1, ax, ay, az):
    
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glLoadIdentity()
    glTranslatef(0,0.0,-7.0)
    #print "cube"
    
    if q1.empty(): 
        pass
    else:
        [ax, ay, az] = q1.get()
        for i in range(q1.qsize()-1):
            q1.get()
        #print q1.qsize()
        
    
    
    
    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(ax))
    yaw_mode = False
    if yaw_mode:
        osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    else:
        osd_line = osd_text

    drawText((-2,-2, 2), osd_line)

    # the way I'm holding the IMU board, X and Y axis are switched 
    # with respect to the OpenGL coordinate system
    
    if yaw_mode:                             # experimental
        glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    else:
        glRotatef(0.0, 0.0, 1.0, 0.0)
    glRotatef(ay ,1.0,0.0,0.0)        # Pitch, rotate around x-axis
    glRotatef(-1*ax ,0.0,0.0,1.0)     # Roll,  rotate around z-axis
    
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glBegin(GL_QUADS)    
    #glColor3f(0.0,1.0,0.0)
    #glActiveTexture(GL_TEXTURE0)

    glTexCoord2f(1.0, 0.0)
    glVertex3f( 1.0, 0.2,-1.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0, 0.2,-1.0)
    glTexCoord2f(0.0, 1.0)        
    glVertex3f(-1.0, 0.2, 1.0)    
    glTexCoord2f(1.0, 1.0)    
    glVertex3f( 1.0, 0.2, 1.0)        
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[1])
    glBegin(GL_QUADS)
    #glColor3f(1.0,0.5,0.0)
    
    glTexCoord2f(1.0, 1.0)    
    glVertex3f( 1.0,-0.2, 1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0,-0.2, 1.0)
    glTexCoord2f(0.0, 0.0)        
    glVertex3f(-1.0,-0.2,-1.0)
    glTexCoord2f(1.0, 0.0)        
    glVertex3f( 1.0,-0.2,-1.0)        
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[2])
    glBegin(GL_QUADS)
    #glColor3f(1.0,0.0,0.0)

    glTexCoord2f(1.0, 1.0)        
    glVertex3f( 1.0, 0.2, 1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glTexCoord2f(0.0, 0.0)        
    glVertex3f(-1.0,-0.2, 1.0)
    glTexCoord2f(1.0, 0.0)        
    glVertex3f( 1.0,-0.2, 1.0)        
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[3])    
    glBegin(GL_QUADS)
    #glColor3f(1.0,1.0,0.0)
    #glBindTexture(GL_TEXTURE_2D, textures[3])
    glTexCoord2f(1.0, 0.0)    
    glVertex3f( 1.0,-0.2,-1.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0, 0.2,-1.0)
    glTexCoord2f(1.0, 1.0)        
    glVertex3f( 1.0, 0.2,-1.0)        
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[4])
    glBegin(GL_QUADS)
    #glColor3f(0.0,0.0,1.0)
    #glBindTexture(GL_TEXTURE_2D, textures[4])
    glTexCoord2f(1.0, 1.0)    
    glVertex3f(-1.0, 0.2, 1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-1.0, 0.2,-1.0)
    glTexCoord2f(0.0, 0.0)        
    glVertex3f(-1.0,-0.2,-1.0)
    glTexCoord2f(0.0, 1.0)        
    glVertex3f(-1.0,-0.2, 1.0)        
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[5])
    glBegin(GL_QUADS)
    #glColor3f(1.0,0.0,1.0)
    #glBindTexture(GL_TEXTURE_2D, textures[5])
    glTexCoord2f(1.0, 0.0)    
    glVertex3f( 1.0, 0.2,-1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 1.0, 0.2, 1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f( 1.0,-0.2, 1.0)
    glTexCoord2f(0.0, 0.0)        
    glVertex3f( 1.0,-0.2,-1.0)        
    glEnd()
    return ax, ay, az

         
def read_data(q1, q2, com):
    #global ax, ay, az, ser, com_flag
    #global data_number
    #line_done = 0
    comname = com.get()
    num  = 0
    print comname
    try: 
        ser = serial.Serial( comname, 115200, timeout=1)
        print "start"
    except:
        return
    com_flag = True
    print "comport open"
    print "xxx"
    # request data by sending a dot
    #ser.write(".")
    #while not line_done:

    while 1:
        try:
            line = ser.readline()
        except:
            print "error"
        angles = line.split(", ")
        #print angles
        if len(angles) == 9 and is_number(angles[0]) and is_number(angles[5]) and is_number(angles[8]):    
            ax = float(angles[0])
            ay = float(angles[1])
            az = float(angles[2])

            bx = float(angles[3])
            by = float(angles[4])
            bz = float(angles[5])

            cx = float(angles[6])
            cy = float(angles[7])
            cz = float(angles[8])
            
            num = (num +1)%100
            if num%1 == 0:
                q1.put([ax, ay, az])
                q2.put([ax, ay, az, bx, by, bz, cx, cy, cz])
            #print ax, ay, az 

def opengl_cube(q1):
    global yaw_mode
    #os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
    #print os.environ['SDL_WINDOWID']

    video_flags = OPENGL|DOUBLEBUF
    #os.environ['SDL_VIDEODRIVER'] = 'windib'
    #end
    # https://stackoverflow.com/questions/23319059/embedding-a-pygame-window-into-a-tkinter-or-wxpython-frame
    pygame.init()
    #pygame.display.init()
    screen = pygame.display.set_mode((500,500), video_flags)
    #screen = pygame.display.get_surface()
    #print "sb"
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
    resize((500,500))
    init()
    #frames = 0
    #ticks = pygame.time.get_ticks()

    #p2 = threading.Thread(target=animate, args=(canvas, root, ))
    #p2.start()
    #lock = threading.Lock()




    
    #ani = animation.FuncAnimation(fig, animate, interval=1000)
    #plt.show()
    #textures
    
    textures = load_texture()
    ax = ay = az =0
    a = 0
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break       
        if event.type == KEYDOWN and event.key == K_z:
            yaw_mode = not yaw_mode
            #ser.write("z")
       
        [ax, ay, az]= draw(textures, q1, ax, ay, az)

        a = a +1
        #print a
        pygame.display.flip()
        #frames = frames+1
def cube_callback():
    global q1
    p = Process(target=opengl_cube, args=(q1, ))
    p.start()
def serial_callback():
    global variable, q1, q2
    global com
    global p_read
    p_read = Process(target=read_data, args=(q1, q2, com))
    #print comName
    com.put(variable.get())
    #print variable.get()
    # p = Process(target=read_data, args=(q1, q2,))
    p_read.start()

def serial_close_callback():
    global p_read
    p_read.terminate()


def main():
    ser1 = 0

    #ax = ay = az = 0.0
    #start
    root = Tk()
    root.title("CILAB IMU GUI")
    #embed = tk.Frame(root, width = 500, height = 500) #creates embed frame for pygame window
    #embed.grid(columnspan = (500), rowspan = 500, row=0, column=0, sticky=E) # Adds grid
    
    # font size
    
    # tkFont.BOLD == 'bold'

    helv12 = tkFont.Font(family='Helvetica', size=8, weight=tkFont.BOLD)

    embed2 = Frame(root, bg= 'blue') #creates embed frame for pygame window
    embed2.grid(columnspan = 500, rowspan = 1000, row =400, column=10,sticky=W) # Adds grid
    #label 
    w = Label(root, text="Comport:")
    w.config(font = helv12)
    w.grid(row=100, column=30,columnspan = 50, rowspan = 70,sticky=W, pady=15)
    #root.grid_rowconfigure(59, weight=100)
    global variable
    variable = StringVar(root)
    #variable.set("COM4") # default value

    o = ttk.Combobox(root, textvariable=variable)
    o['values'] = ("COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9","COM10", "COM11", "COM12", "COM13", "COM14", "COM15")
    #o.config( font = helv12)
    o.grid(row=100, column=80,columnspan = 50, rowspan = 70,sticky=W, pady=15)
    o.current(0)
    #o = OptionMenu(root, variable, "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9")
    #o.config( font = helv12)
    #o.grid(row=100, column=90,columnspan = 50, rowspan = 70,sticky=W, pady=15)

    b1 = Button(root, text="Open", command= serial_callback)
    #print id(p)
    b1.config( font = helv12)
    b1.grid(row=100, column=150,columnspan = 50, rowspan = 70,sticky=W, pady=15)

    b2 = Button(root, text="Close", command= serial_close_callback )
    b2.config( font = helv12)
    b2.grid(row=100, column=210,columnspan = 50, rowspan = 70,sticky=W)
    b3 = Button(root, text="Show Cube", command= cube_callback )
    b3.config( font = helv12)
    b3.grid(row=100, column=260,columnspan = 80, rowspan = 70,sticky=W)
    


    #while com_flag == False:
    #    root.update()
    root.update()
    canvas = FigureCanvasTkAgg(fig, master=embed2)
    canvas.get_tk_widget().grid(row=200, column=260,columnspan = 1020, rowspan = 1200,sticky=W)
    sleep(0.3)
    while 1:
        
        animate2(q2)
        canvas.show()

        root.update()
        #sleep(0.1)
if __name__ == '__main__': 
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        freeze_support()
    main()

