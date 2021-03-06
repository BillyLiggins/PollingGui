#!/usr/bin/python
#import matplotlib
#matplotlib.use("TkAgg")
#
import os
import numpy as np
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure
import Tkinter
import Tkinter as tk
import ttk
import tkFont
from snotdaq import DataStream
from snotdaq.datastream import *
import time
import socket
import struct
import time 
import sys
import tkMessageBox
import webbrowser
##fix for monug2
#from datastream import parse_cmos_record


# Imports for PSQL access
import psycopg2
import psycopg2.extras
import psycopg2.extensions


class PasswordDialog(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        #top = self.top = tk.Toplevel(parent)
        tk.Label(self, text="database host").grid(row=0,column=0, sticky=tk.W,padx=10)
        self.a = tk.Entry(self)
        self.a.insert(0,'192.168.80.120')
        # self.a.insert(0,'pgsql.snopl.us')
        self.a.grid(row=0,column=1, sticky=tk.W)

        tk.Label(self, text="database name").grid(row=1,column=0, sticky=tk.W,padx=10)
        self.b = tk.Entry(self)
        self.b.insert(0,'detector')
        self.b.grid(row=1,column=1, sticky=tk.W)

        tk.Label(self, text="database user").grid(row=2,column=0, sticky=tk.W,padx=10)
        self.c = tk.Entry(self)
        # self.c.insert(0,'alarm_gui')
        self.c.insert(0,'snoplus')
        self.c.grid(row=2,column=1, sticky=tk.W)

        tk.Label(self, text="database password").grid(row=3,column=0, sticky=tk.W,padx=10)
        self.d = tk.Entry(self,show='x')
        self.d.insert(0,'')
        self.d.focus_set()
        self.d.bind('<Return>', self.check)
        self.d.grid(row=3,column=1, sticky=tk.W)

        b = tk.Button(self, text="Submit", command=self.check)
        b.grid(row=4,columnspan=2)


    def check(self, *args):
        self.host = self.a.get()
        self.name = self.b.get()
        self.user = self.c.get()
        self.password = self.d.get()
        try:
            # Try establishing connection. This is the sure way to know if the
            # password is correct.
            conn = psycopg2.connect('dbname=%s user=%s password=%s host=%s connect_timeout=5'
                                    % (self.name, self.user, self.password, self.host))
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            conn.close()
            self.destroy()
        except psycopg2.Error as e:
            tkMessageBox.showerror('Error',('Unable to connect! {0} \nMight be due to no connection to the DB or a wrong password').format(e))

class rect():
   
    def __init__(self, root,canvas,x1,y1,x2,y2,crate,card,channel,mother):
        # self.master= root
        self.mother = mother
        self.master=mother.master
        self.canvas = mother.crateView
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = self.x2-self.x1
        self.height= self.y2-self.y1
        self.word="0"
        self.unit=""
        self.textID=0
        self.colors=["black","green","red"]
        self.invertedColors=["white","black","white"]
        # self.colors=colors
        # self.invertedColors=invertedColors
        self.crate= crate
        self.card=card
        self.channel= channel
        #=========ToolTipOptions============
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.id = None
        self.tw = None
	self.unitScale={"":0,"k":3,"M":6,"B":9}
	self.colorNA = "black"
	self.color_old = None
	self.textColor_old = None
	self.outlineColor_old = None

        self.color_pulledResistor   = self.mother.color_pulledResistor
        self.color_LowOcc           = self.mother.color_LowOcc        
        self.color_ZeroOcc          = self.mother.color_ZeroOcc       
        self.color_LowGain          = self.mother.color_LowGain       
        self.color_BadBase          = self.mother.color_BadBase
        self.color_openRelay        = self.mother.color_openRelay


        self.rectID=self.mother.crateView.create_rectangle(x1,y1,x2,y2,fill='black')
        # self.rectID=canvas.create_rectangle(x1,y1,x2,y2,fill='black')
        self.textID= self.canvas.create_text((self.x1+self.width/2,self.y1+self.height/2),text=(self.word+self.unit),fill='white',font= ("helvetica", 8))

        self.toolTipText="Card %i, Channel %i " % (self.card,self.channel)

        self.canvas.tag_bind(self.rectID,"<Enter>", self.enter)
        self.canvas.tag_bind(self.rectID,"<Leave>", self.leave)
        self.canvas.tag_bind(self.rectID,"<B1-Motion>",self.enter)
        self.canvas.tag_bind(self.textID,"<Enter>", self.enter)
        self.canvas.tag_bind(self.textID,"<Leave>", self.leave)
        self.canvas.tag_bind(self.textID,"<B1-Motion>",self.enter)

    def updateText(self):
        self.toolTipText="Card %i, Channel %i " % (self.card,self.channel)
        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["nohvpmt"]==True:
            self.toolTipText=self.toolTipText+", Pulled resistor" 
        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["open"]==True:
            self.toolTipText=self.toolTipText+", Open Relay" 
        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["type"]=="Low Gain":
            self.toolTipText=self.toolTipText+", Low Gain" 
        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["lowOcc"]==True:
            self.toolTipText=self.toolTipText+", Low Occ" 
        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["zeroOcc"]==True:
            self.toolTipText=self.toolTipText+", Zero Occ" 
        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["badbase"]==True:
            self.toolTipText=self.toolTipText+", Bad Base Current" 

        self.canvas.itemconfigure(self.textID,text=(self.word+self.unit))
    
    def updateColor(self,bounds):
	#hack to get absolute values.
        if self.mother.color_Schemes_header.get()=="Absolute Values":
            bounds = self.mother.absoluteLimits

        textColor="black"
        if self.word =='N/A' and self.colorNA!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.colorNA)
            self.canvas.itemconfigure(self.textID,fill='white')
            self.canvas.itemconfigure(self.rectID,outline=self.colorNA)
	    self.color_old = self.colorNA
	    self.textColor_old = "white"
            return
	elif self.word =='N/A':
	    return
        #self.mother.dropDown.itemconfigure(self.mother.text_bounds, text = "Bounds: %f to %f"%(bounds[0],bounds[1]))

        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["open"]==True  and self.color_openRelay!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.color_openRelay)
            self.canvas.itemconfigure(self.textID,fill='black')
            self.canvas.itemconfigure(self.rectID,outline="black")
	    self.color_old = self.color_openRelay
	    self.textColor_old = "black"
            return
	elif self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["open"]==True:
	    return

        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["nohvpmt"]==True  and self.color_pulledResistor!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.color_pulledResistor)
            self.canvas.itemconfigure(self.textID,fill='black')
            self.canvas.itemconfigure(self.rectID,outline="black")
	    self.color_old = self.color_pulledResistor
	    self.textColor_old = "black"
            return
	elif self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["nohvpmt"]==True:
	    return

        if  self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["type"]=="Low Gain" and self.color_LowGain!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.color_LowGain)
            self.canvas.itemconfigure(self.textID,fill='white')
            self.canvas.itemconfigure(self.rectID,outline=self.color_LowGain)
	    self.color_old = self.color_LowGain
	    self.textColor_old = "white"
            return
	elif self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["type"]=="Low Gain":
	    return

        if  self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["lowOcc"]==True and self.color_LowOcc!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.color_LowOcc)
            self.canvas.itemconfigure(self.textID,fill='white')
            self.canvas.itemconfigure(self.rectID,outline=self.color_LowOcc)
	    self.color_old = self.color_LowOcc
	    self.textColor_old = "white"
            return
	elif self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["lowOcc"]==True:
	    return

        if  self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["zeroOcc"]==True and self.color_ZeroOcc!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.color_ZeroOcc)
            self.canvas.itemconfigure(self.textID,fill='white')
            self.canvas.itemconfigure(self.rectID,outline=self.color_ZeroOcc)
	    self.color_old = self.color_ZeroOcc
	    self.textColor_old = "white"
            return
	elif self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["zeroOcc"]==True:
	    return

        if  self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["badbase"]==True and self.color_BadBase!=self.color_old:
            self.canvas.itemconfigure(self.rectID,fill=self.color_BadBase)
            self.canvas.itemconfigure(self.textID,fill='white')
            self.canvas.itemconfigure(self.rectID,outline=self.color_BadBase)
	    self.color_old = self.color_BadBase
	    self.textColor_old = "white"
            return
	elif self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["badbase"]==True:
	    return

#        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["pmthv"]==True:
#            color="gray"
#        if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["lowgain"]==True:
#            color="blue"

	if float(self.word)*10**self.unitScale[self.unit] < bounds[0]:
	        color = self.colors[0]
	        textColor = self.invertedColors[0]
	elif bounds[0] <= float(self.word)*10**self.unitScale[self.unit] < bounds[1]:
	        color = self.colors[1]
	        textColor = self.invertedColors[1]
	elif bounds[1]<=float(self.word)*10**self.unitScale[self.unit]:
	        color = self.colors[2]
	        textColor = self.invertedColors[2]

        if color!=self.color_old or textColor != self.textColor_old:
		self.canvas.itemconfigure(self.rectID,fill=color)
	    	#self.canvas.itemconfigure(self.rectID,activefill="gold")
	    	#self.canvas.itemconfigure(self.textID,activefill='white')
	    	self.canvas.itemconfigure(self.rectID,outline=color)
	    	self.canvas.itemconfigure(self.textID,fill=textColor)
	    	
	    	self.color_old = color
	    	self.textColor_old = textColor	
        
    def enter(self, event=None):
        self.mother.dropDown.delete(self.mother.mousePosID)
        self.schedule()

        #self.mother.mousePos = tk.Label(self.mother.dropDown, text = "Crate %s , Card %s , Channel %s"%(self.crate.get(),self.card,self.channel),fg = "black" ,bg="gray", width=25,height=1,font= ("helvetica", 12))

        self.mousePosText="Crate %s , Card %s , Channel %s"%(self.crate.get(),self.card,self.channel)
        if self.crate.get() != "-1":
            if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["nohvpmt"]==True:
                self.mousePosText=self.mousePosText+", \nPulled resistor" 
            if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["type"]=="Low Gain":
                self.mousePosText=self.mousePosText+", \nLow Gain" 
            if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["lowOcc"]==True:
                self.mousePosText=self.mousePosText+", \nLow Occupancy" 
            if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["zeroOcc"]==True:
                self.mousePosText=self.mousePosText+", \nZero Occupancy" 
            if self.mother.channelState[str(self.crate.get())][str(self.card)][str(self.channel)]["badbase"]==True:
                self.mousePosText=self.mousePosText+", \nBad Base Current" 
        self.mother.mousePos = tk.Label(self.mother.dropDown, text =self.mousePosText ,fg = "black" ,bg="gray", width=30,height=7,font= ("helvetica", 12))
        self.mother.mousePosID=self.mother.dropDown.create_window(self.mother.cell_canvas_width/6,0.1*self.mother.cell_canvas_height,window=self.mother.mousePos)


    def leave(self, event=None):
        self.mother.dropDown.delete(self.mother.mousePosID)

        self.mother.mousePos = tk.Label(self.mother.dropDown, text = "Crate %s , Card %s , Channel %s"%("-","-","-"),fg = "black" ,bg="gray", width=25,height=1,font= ("helvetica", 12))
        self.mother.mousePosID=self.mother.dropDown.create_window(self.mother.cell_canvas_width/6,0.1*self.mother.cell_canvas_height,window=self.mother.mousePos)

        self.unschedule()
        self.hidetip()


    def schedule(self):
        self.unschedule()
        self.id = self.master.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            # self.widget.after_cancel(id)
            self.master.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        # x, y, cx, cy = self.widget.bbox("insert")
        # x, y, cx, cy = self.root.bbox("insert")
        x, y, cx, cy = self.canvas.bbox(self.rectID)
        x += self.canvas.winfo_rootx() + 25
        y += self.canvas.winfo_rooty() + 20
        # x += self.widget.winfo_rootx() + 25
        # y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        # self.tw = tk.Toplevel(self.widget)
        self.tw = tk.Toplevel(self.canvas)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.toolTipText, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class App():

    """Docstring for App. """

    def __init__(self):
        """TODO: to be defined1. """

        self.bounds= [5,95]
        self.absoluteLimits= [0,1000]
        self.margin_left = 40
        self.margin_right = 40
        self.margin_top = 100
        self.margin_bottom = 50

        self.cell_width = 40
        self.cell_height = 25
        self.cell_padding = 0.2*self.cell_height
        self.PD_padding = 2
        self.crate_x_padding= 10
        self.crate_y_top_padding= 10
        self.crate_y_bottom_padding= 10

        self.master = Tkinter.Tk()
        self.master.title("Polling GUI")
        self.master.resizable(0,0)

        self.cell_canvas_width =  self.margin_left+2*self.crate_x_padding + 16*( self.cell_width + 2* self.cell_padding)+self.margin_right
        self.cell_canvas_height = self.margin_top+32*(self.cell_height+2*self.cell_padding)+3*self.PD_padding+self.crate_y_top_padding+self.crate_y_bottom_padding+self.margin_bottom


        ws = self.master.winfo_screenwidth() # width of the screen
        hs = self.master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - ((self.cell_canvas_width*1.3)/2)
        y = (hs/2) - (self.cell_canvas_height/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.master.geometry('%dx%d+%d+%d' % ((self.cell_canvas_width*1.3),self.cell_canvas_height, x, y))
        
        try:
            #pass
            os.environ['PGOPTIONS'] = '-c statement_timeout=10000' #in ms
            self.conn = psycopg2.connect('dbname=%s user=%s host=%s connect_timeout=5 '
                                    % ("detector", "snoplus","dbug" ))
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            #self.conn = psycopg2.connect('dbname=%s user=%s host=%s connect_timeout=5 '
            #                       % ("detector", "snoplus","192.168.80.120" ))
            #self.conn = psycopg2.connect()
        except Exception as e:
            self.d = PasswordDialog(self.master)
            self.d.pack()
            self.master.wait_window(self.d)

            # Set up the connection to the database
            os.environ['PGOPTIONS'] = '-c statement_timeout=10000' #in ms
            self.conn = psycopg2.connect('dbname=%s user=%s password=%s host=%s connect_timeout=5 '
                                    % (self.d.name, self.d.user, self.d.password, self.d.host))
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)


        print "Width = ",self.cell_canvas_width
        print "height = ",self.cell_canvas_height

        self.sub_opinions=["BASE","CMOS"]

        self.numOfSlots= 16
        self.numOfChannels= 32
        self.numOfCrates = 18+1
        self.millnames = ['','k','M','B','T']
	self.unitScale={"":0,"k":3,"M":6,"B":9}
        self.clearingTime=5
        self.counter=0
        self.diff=None

        self.color_pulledResistor ='grey'
        self.color_LowGain ='#707070'
        self.color_LowOcc ='#4D4D4D'
        self.color_ZeroOcc ='#2E2E2E'
        self.color_BadBase = '#00b2a9'
        self.color_openRelay = 'white'

        self.findChannelState()
        self.init_datastream()
        self.init_dropDown()
        self.init_crateView()
        self.init_crate()

        self.update_crates()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()

    def on_closing(self):
            if tkMessageBox.askokcancel("Quit",
                                    "Close?"):
	       #Taken out to work on monug2
               #self.data.disconnect()
               self.master.destroy()



    def init_datastream(self):

        # When using the polling gui from a remote station the timeout may need to be extended.
        self.data = DataStream('192.168.80.124', name='polling_gui', subscriptions=['BASE','CMOS'],timeout=0.5)
        self.data.connect()

        self.newData={} 
        for polling in self.sub_opinions:
            self.newData[str(polling)]={}
            for crate in range(self.numOfCrates):
                self.newData[str(polling)][str(crate)]={}
                for card in range(self.numOfSlots):
                    self.newData[str(polling)][str(crate)][str(card)]={}
                    for channel in range(self.numOfChannels):
                        self.newData[str(polling)][str(crate)][str(card)][str(channel)]={}
                        self.newData[str(polling)][str(crate)][str(card)][str(channel)]['value']=None
                        self.newData[str(polling)][str(crate)][str(card)][str(channel)]['timestamp']=None
                        self.newData[str(polling)][str(crate)][str(card)][str(channel)]['init_value']=None
        print "init dict"

    def clearTime(self):
        for polling in self.sub_opinions:
            for crate in range(self.numOfCrates):
                for card in range(self.numOfSlots):
                    for channel in range(self.numOfChannels):
                        # This checks if the timestamp has been stamped and clears the value if it has been to long.
                        if  self.newData[str(polling)][str(crate)][str(card)][str(channel)]['value']!=None and time.time()-self.newData[str(polling)][str(crate)][str(card)][str(channel)]['timestamp']>self.clearingTime:
                            self.newData[str(polling)][str(crate)][str(card)][str(channel)]['value']=None
                            self.newData[str(polling)][str(crate)][str(card)][str(channel)]['unit']=None

    def pullData(self):
        # print 'pulling data'
        self.getRecord()
        if self.record:
            self.parseRecord()
        #self.clearTime()

    def getRecord(self):
        """TODO: Docstring for pollBaseCurrents.
        :returns: TODO

        """
        # print 'getRecord()'

        self.counter=self.counter+1
        try:
            self.id, self.record = self.data.recv_record()
        except socket.timeout:
            if self.counter%100==0:
                return
            #self.getRecord()
            return
        except (socket.error, RuntimeError) as e:
            print "error receiving record: %s" % e
            try:
                print "connecting to data stream..."
                self.data.connect()
            except socket.error as e:
                print "error connecting to data stream: %s" % e
            else:
                print "connected!"
            #master.after(10000, update_fifo_levels, master)
            time.sleep(1)
            self.getRecord()
            
            return

        #print "id = ", self.id
        #print "record= ", self.record
        #
        if self.id not in self.sub_opinions :
             print 'Not in subs'
             self.getRecord()
             return
         
    def parseRecord(self):

        #struct CMOSLevels {
        #    uint32_t crate;
        #    uint32_t slotMask;
        #    uint32_t channelMasks[16];
        #    uint32_t errorFlags;
        #    uint32_t counts[8*32];
        #    uint32_t busyFlags[16];
        #};

        #struct BaseCurrentLevels {
        #    uint32_t crate;
        #    uint32_t slotMask;
        #    uint32_t channelMasks[16];
        #    uint32_t errorFlags;
        #    uint8_t pmtCurrent[16*32];
        #    uint8_t busyFlags[16*32];
        #};


        if self.id == 'BASE':
            unpackedData= struct.unpack(">LL16LL512B512B",self.record)
            crate=unpackedData[0]
            slotMask=unpackedData[1]
            channelMask=np.array(unpackedData[2:2+16])
            errorFlag=unpackedData[18]
            pmtCurrents=np.split(np.array(unpackedData[19:19+512])-127,16)
            busyFlags=np.split(np.array(unpackedData[19+512:]),16)

            #print "crate = ", type(crate)
            #print "slotMask = ", hex(slotMask)
            #print "ChannelMask = ", channelMask
            #print "errorFlags = ", errorFlag
            #print "pmtCurrents = ",pmtCurrents[0][0]
            #print "type(pmtCurrents) = ",type(pmtCurrents[0][0])
            #print "busyFlags= ",busyFlags

            for card in range(16):
                if (1<<card)&slotMask ==(1<<card):
                    for channel in range(32):
                        if (1<<channel)&channelMask[card]==(1<<channel):
                                if not busyFlags[card][channel]:
                                    self.newData['BASE'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
                                    self.newData['BASE'][str(crate)][str(card)][str(channel)]['value']=float(pmtCurrents[card][channel])
            # print 'polled BASE from crate ',crate


        if self.id == 'CMOS':
        # What happens when a CMOS rate is received.
            #unpackedData= struct.unpack(">LL16LL256L16L",self.record)
            #crate=unpackedData[0]
            #slotMask=unpackedData[1]
            #channelMask=np.array(unpackedData[2:2+16])
            #errorFlag=unpackedData[18]
            ##hack ask tony about polling one card.
            ##counts =np.split(np.array(unpackedData[19:19+256]),16)
            #counts =np.split(np.array(unpackedData[19:19+256]),16)
            #busyFlags=np.split(np.array(unpackedData[19+256:]),16)

            crate, counts, errorFlag = parse_cmos_record(self.record) 

            if not errorFlag:
                for card in range(16):
                    if counts[card]==None:
                        # print "counts[card] = ", counts[card], " got continued"
                        continue
                    for channel in range(32):
				# Ask whether the CMOS record has been received and successfully parsed. If so then initialise it and break.
				if self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']==None or self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value']==None:
				    self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value']=counts[card][channel]
				    self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
				    continue

				
				self.newData['CMOS'][str(crate)][str(card)][str(channel)]['value']=( counts[card][channel]-self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value'] )/(time.time()-self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp'])


				self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value']=counts[card][channel]
				self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()

            # print 'polled CMOS from crate ',crate
        

    def init_dropDown(self):
        """TODO: Docstring for init_dropDown.

        :f: TODO
        :returns: TODO

        """
        
        self.dropDown= Tkinter.Canvas(self.master, width=self.cell_canvas_width/3, height=self.cell_canvas_height,background='gray')
        self.dropDown.grid(row=0,column=0,sticky=Tkinter.N)


        self.text_polling = tk.Label(self.dropDown, text="Polling : ",bg = "gray" ,fg="black", width=12,height=1,font= ("helvetica", 12))
        self.dropDown.create_window((self.cell_canvas_width/6),0.2*self.cell_canvas_height-24,window=self.text_polling)

        self.poll_options_header= Tkinter.StringVar(self.master)
        self.poll_options_header.set("Pick Poll") # default value
        self.poll_dropdown= Tkinter.OptionMenu(self.dropDown,self.poll_options_header, *self.sub_opinions, command = self.enable_menu)
        self.pollId = self.dropDown.create_window(self.cell_canvas_width/6,0.2*self.cell_canvas_height,window=self.poll_dropdown)
        print "pollId = ",self.pollId

        self.text_bounds = tk.Label(self.dropDown, text="Bounds ",bg = "gray" ,fg="black", width=22,height=1,font= ("helvetica", 12))
        self.text_bounds_id = self.dropDown.create_window((self.cell_canvas_width/6),0.7*self.cell_canvas_height-24,window=self.text_bounds)

        self.crates_nums=[format(x,'n') for x in range(self.numOfCrates)]
        self.crate_options_header= Tkinter.StringVar(self.master)
        self.crate_options_header.set(-1) # default value
        self.crate_options= Tkinter.OptionMenu(self.dropDown,self.crate_options_header, *self.crates_nums)
        self.crate_options["state"] = 'disabled'

        self.crateID = self.dropDown.create_window(self.cell_canvas_width/6,0.3*self.cell_canvas_height,window=self.crate_options)
        self.text_crate = tk.Label(self.dropDown, text="Crate # : ",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
        self.dropDown.create_window((self.cell_canvas_width/6),0.3*self.cell_canvas_height-24,window=self.text_crate)

        #=============Legend section=================
        self.legID1=self.dropDown.create_rectangle(self.cell_canvas_width/12,0.5*self.cell_canvas_height-10,self.cell_canvas_width*3/12,0.5*self.cell_canvas_height+10,outline="black",fill="black")
        self.legID2=self.dropDown.create_rectangle(self.cell_canvas_width/12,0.5*self.cell_canvas_height+10,self.cell_canvas_width*3/12,0.5*self.cell_canvas_height+30,outline="green",fill="green")
        self.legID3=self.dropDown.create_rectangle(self.cell_canvas_width/12,0.5*self.cell_canvas_height+30,self.cell_canvas_width*3/12,0.5*self.cell_canvas_height+50,outline="red" ,fill="red")

        self.leg_lower = self.dropDown.create_text(self.cell_canvas_width/6,0.5*self.cell_canvas_height,text=str(self.bounds[0])+"% < x", fill = "white" ,font= ("helvetica", 12))
        self.leg_middle= self.dropDown.create_text(self.cell_canvas_width/6,0.5*self.cell_canvas_height+22,text=str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%", fill = "black",font= ("helvetica", 12))
        self.leg_high  = self.dropDown.create_text(self.cell_canvas_width/6,0.5*self.cell_canvas_height+44, text=str(self.bounds[1])+"% < x", fill = "white" ,font= ("helvetica", 12))

        self.text_crate = tk.Label(self.dropDown, text="Filter type :",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
        self.dropDown.create_window((self.cell_canvas_width/6),0.555*self.cell_canvas_height,window=self.text_crate)

	self.lowEntry = Tkinter.Entry(self.dropDown, width=5)
	self.lowEntryLabel= Tkinter.Label(self.dropDown,text="low",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
        self.dropDown.create_window(self.cell_canvas_width/12,0.58*self.cell_canvas_height+44,window=self.lowEntryLabel)
        self.LowerBoundEntryID=self.dropDown.create_window(self.cell_canvas_width/12,0.6*self.cell_canvas_height+44,window=self.lowEntry)

	self.highEntry = Tkinter.Entry(self.dropDown, width=5)
	self.highEntryLabel= Tkinter.Label(self.dropDown,text="high",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
       	self.dropDown.create_window(3*self.cell_canvas_width/12,0.58*self.cell_canvas_height+44,window=self.highEntryLabel)
        self.UpperBoundEntryID=self.dropDown.create_window(3*self.cell_canvas_width/12,0.6*self.cell_canvas_height+44,window=self.highEntry)

        self.colorSchemes=["Percentage","Absolute Values"]
        self.color_Schemes_header= Tkinter.StringVar(self.master)
        self.color_Schemes_header.set("Percentage") # default value
        self.color_Schemes= Tkinter.OptionMenu(self.dropDown,self.color_Schemes_header, *self.colorSchemes,command=self.clearEntry)
        self.color_Schemes["state"] = 'disabled'
        self.dropDown.create_window((self.cell_canvas_width/6),0.575*self.cell_canvas_height,window=self.color_Schemes)

        #===PMT Type===
        legList = [[self.color_openRelay, "Open Relay","black"],
                   [self.color_pulledResistor, "Pulled Resistor","black"],
                   [self.color_BadBase, "Bad Base Currents","black"],
                   [self.color_LowGain, "Low Gain","white"],
                   [self.color_LowOcc, "Low Occupancy","white"],
                   [self.color_ZeroOcc, "Zero Occupancy","white"]
                  ]
        shift = 0
        for i, entry in enumerate(legList):
            self.dropDown.create_rectangle(self.cell_canvas_width/12,0.7*self.cell_canvas_height+(i*25)-shift,self.cell_canvas_width*3/12,0.7*self.cell_canvas_height+(25+i*25)-shift, outline="black",fill=entry[0])
            self.dropDown.create_text(self.cell_canvas_width/6,0.7*self.cell_canvas_height+(15+i*25)-shift,text=entry[1],fill = entry[2],font= ("helvetica", 12))

        #==========crate options==========
        self.mousePos = tk.Label(self.dropDown, text="Crate ",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
        self.mousePosID=self.dropDown.create_window(self.cell_canvas_width/6,0.1*self.cell_canvas_height,window=self.mousePos)
        #===========Github Button ========
	self.githubButton= Tkinter.Button(self.dropDown,text="Report issue\n on github",command=self.report_bug)
        self.githubButtonID=self.dropDown.create_window(self.cell_canvas_width/6,0.9*self.cell_canvas_height,window=self.githubButton)

    def clearEntry(self,entry):
        self.highEntry.delete(0,'end')
        self.lowEntry.delete(0,'end')

    def report_bug(self):
        # This link will require the user to login to github to report
        # the issue.
        if tkMessageBox.askokcancel("Report",
                                    "You will be directed to GitHub (login required)."):
            webbrowser.open_new("https://github.com/BillyLiggins/PollingGui/issues")
    def updateBounds(self):
        if self.color_Schemes_header.get() == "Percentage":
            if self.poll_options_header.get()=="BASE":
                self.bounds=[5,95]
            elif self.poll_options_header.get()=="CMOS":
                self.bounds=[3,97]

            if self.lowEntry.get():
                    try:
                        low= float(self.lowEntry.get())
                        if float(low<float(self.bounds[1])) and float(low)<=100 and float(low)>=0:
                                    self.bounds[0]=float(self.lowEntry.get())
                    except ValueError:
                        return

                    #if float(self.lowEntry.get())<float(self.bounds[1]) and float(self.lowEntry.get())<=100 and float(self.lowEntry.get())>=0:
            if self.highEntry.get():
                    if self.highEntry.get():
                            try:
                                high= float(self.highEntry.get())
                                if float(high)>float(self.bounds[0]) and float(high)<=100 and float(high)>=0:
                                     self.bounds[1]=float(self.highEntry.get())
                            except ValueError:
                                return
                    
            # if self.lowEntry.get() or self.highEntry.get() :
            #         self.dropDown.itemconfigure(self.leg_lower,text=str(self.bounds[0])+"% < x")
            #         self.dropDown.itemconfigure(self.leg_middle,text=str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%")
            #         self.dropDown.itemconfigure(self.leg_high,text="x < "+str(self.bounds[1])+"%")
            # else: 
            #         return
            self.dropDown.itemconfigure(self.leg_lower,text="x < "+str(self.bounds[0])+"% ")
            self.dropDown.itemconfigure(self.leg_middle,text=str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%")
            self.dropDown.itemconfigure(self.leg_high,text=str(self.bounds[1])+"% < x")

        elif self.color_Schemes_header.get() == "Absolute Values":
            if self.poll_options_header.get()=="BASE":
                self.absoluteLimits=[30,90]
            elif self.poll_options_header.get()=="CMOS":
                self.absoluteLimits=[100,100000]
            if self.lowEntry.get():
                    try:
                        low= float(self.lowEntry.get())
                        if float(low<float(self.absoluteLimits[1])):
                                    self.absoluteLimits[0]=float(self.lowEntry.get())
                    except ValueError:
                        return

                    #if float(self.lowEntry.get())<float(self.bounds[1]) and float(self.lowEntry.get())<=100 and float(self.lowEntry.get())>=0:
            if self.highEntry.get():
                    if self.highEntry.get():
                            try:
                                high= float(self.highEntry.get())
                                if float(high)>float(self.absoluteLimits[0]):
                                     self.absoluteLimits[1]=float(self.highEntry.get())
                            except ValueError:
                                return
                    
            # if self.lowEntry.get() or self.highEntry.get():
            #         self.dropDown.itemconfigure(self.leg_lower,text=str(self.absoluteLimits[0])+" < x")
            #         self.dropDown.itemconfigure(self.leg_middle,text=str(self.absoluteLimits[0])+" < x < "+str(self.absoluteLimits[1])+"")
            #         self.dropDown.itemconfigure(self.leg_high,text="x < "+str(self.absoluteLimits[1])+"")
            # else: 
            self.dropDown.itemconfigure(self.leg_lower,text=str(self.absoluteLimits[0])+" < x")
            self.dropDown.itemconfigure(self.leg_middle,text=str(self.absoluteLimits[0])+" < x < "+str(self.absoluteLimits[1])+"")
            self.dropDown.itemconfigure(self.leg_high,text="x < "+str(self.absoluteLimits[1])+"")
            #         return
        else:
            return

    def init_crateView(self):
        """TODO: Docstring for init_crateView.
        :returns: TODO

        """
        
        self.crateView = Tkinter.Canvas(self.master, width=self.cell_canvas_width, height=self.cell_canvas_height,background='gray')
        self.crateView.grid(row=0,column=1)
        self.dictOfCells={}
        self.crate_options_number_for_tooltips="-1"
        self.crate_options_number="-1"

    def makePlot(self):

        f=Figure(figsize=(1,1),dpi=200)
        a = f.add_subplot(111)
        a.hist(self.numbers,50)
        a.set_xlabel("dist")

        
        canvas = FigureCanvasTkAgg(f, master=self.dropDown)
        canvas.show()
        plotId = canvas.get_tk_widget()
        # self.mother.mousePosID=self.mother.dropDown.create_window(self.mother.cell_canvas_width/6,0.1*self.mother.cell_canvas_height,window=self.mother.mousePos)
        self.dropDown.create_window(self.cell_canvas_width/6,0.8*self.cell_canvas_height,window=plotId, height=100, width=100)

    # toolbar = NavigationToolbar2TkAgg(canvas, root)
    # toolbar.update()
    # canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


    def millify(self,n):
        """This function rounds and millifies a number, mainly for CMOS rates"""
        n = float(n)
        millidx = max(0,min(len(self.millnames)-1,
                            int(np.floor(0 if n == 0 else np.log10(abs(n))/3))))

        return ["%.1f"%(n / 10**(3 * millidx)), self.millnames[millidx]]


    def update_crates(self):
        """TODO: Docstring for update_crates.
        :arg1: TODO
        :returns: TODO
        """
        if (self.crate_options_number_for_tooltips!=self.crate_options_header.get() ):

            self.crateView.itemconfigure(self.labelText,text="%s on Crate %s"%(self.poll_options_header.get(),self.crate_options_header.get()))
            self.crate_options_number_for_tooltips=self.crate_options_header.get()

        if (self.crate_options_number!=self.crate_options_header.get()):
            self.numbers=[]
            for card in range(self.numOfSlots):
                for channel in range(self.numOfChannels):
                    if self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'] != None and time.time()-self.newData[str(self.poll_options_header.get())][str(self.crate_options_header.get())][str(card)][str(channel)]['timestamp']<self.clearingTime:
		    	num,unit = self.millify(self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'])

                        if float(num)*10**self.unitScale[str(unit)] not in self.numbers:
                            self.numbers.append(float(num)*10**self.unitScale[str(unit)])
                    else:
                        self.numbers.append(0)

            for card in range(self.numOfSlots):
                for channel in range(self.numOfChannels):
                    if self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'] == None:
                        self.dictOfCells[str(card)][channel].word="N/A"
                        self.dictOfCells[str(card)][channel].unit=""
                    elif time.time()-self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['timestamp']>self.clearingTime:
                        self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'] = None

                    else:
                        self.dictOfCells[str(card)][channel].word,self.dictOfCells[str(card)][channel].unit=self.millify(self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'])


                    self.dictOfCells[str(card)][channel].updateColor(self.percentile(np.array(self.numbers),self.bounds))
                    #self.dictOfCells[str(card)][channel].updateColor((10,1000))
                    self.dictOfCells[str(card)][channel].updateText()


        self.record=None
        self.pullData()
	self.updateBounds()
        # self.makeData()
        #the master after time is important for the tooltips and the data.
        self.master.after(1, self.update_crates)


    def init_crate(self):
        """TODO: Docstring for init_crate.
        :returns: TODO

        """
                
        # crateView.create_text(margin_left,0.5*margin_top,text="see here",font=('helvetica', 12, "bold"), anchor=Tkinter.W)
        # print "margin_left = ",margin_left

        for card in range(self.numOfSlots):
            x1 = self.margin_left+ self.crate_x_padding + card*( self.cell_width + 2* self.cell_padding)    # crate_width + card*card_width
            x2 = x1 + self.cell_width
            for channel in range(self.numOfChannels-1,-1,-1):

                # y1 = self.margin_top+ (self.numOfChannels-1-channel)*(self.cell_height+2*self.cell_padding)+((self.numOfChannels-1- channel)-(self.numOfChannels-1-channel)%8)*self.PD_padding+self.crate_y_top_padding
                # y2 = y1 - self.cell_height
                y1 = self.margin_top+ channel*(self.cell_height+2*self.cell_padding)+(channel-channel%8)*self.PD_padding+self.crate_y_top_padding
                y2 = y1 - self.cell_height

                # This is pretty bad but the reason you give self.numOfChannels-1-channel as the channel number is to get the layout correct.
                self.dictOfCells.setdefault(str(card),[]).append(rect(self.master,self.crateView,x1,y1,x2,y2,self.crate_options_header,card,self.numOfChannels-1-channel,self))

        self.labelText= self.crateView.create_text((self.margin_left+2*self.cell_padding,0.5*self.margin_top),text="*** on Crate ***",fill='black',font= ("helvetica", 18),anchor= Tkinter.W)
    
        self.warningText= self.crateView.create_text((self.margin_left+200,0.5*self.margin_top),text="*** Poll < 5 crates when using this GUI ***",fill='red',font= ("helvetica", 18),anchor= Tkinter.W)

    def pmt_type_description(self,pmt_type):
        """
        Converts a PMT type -> useful description.
        """
        active, pmt_type = pmt_type & 0x1, pmt_type & 0xfffe

        if pmt_type == 0x2:
            return "Normal"
        elif pmt_type == 0x4:
            return "Rope"
        elif pmt_type == 0x8:
            return "Neck"
        elif pmt_type == 0x10:
            return "FECD"
        elif pmt_type == 0x20:
            return "Low Gain"
        elif pmt_type == 0x40:
            return "OWL"
        elif pmt_type == 0x80:
            return "Butt"
        elif pmt_type == 0x12:
            return "Petal-less PMT"
        elif pmt_type == 0x00:
            return "No PMT"
        elif pmt_type == 0x100:
            return "HQE PMT"
        else:
            return "Unknown type 0x%04x" % pmt_type


    def findChannelState(self):
        """TODO: Docstring for findChannelState.
        :returns: TODO

        """
        
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT crate,slot,channel,type FROM pmt_info;")
        self.info= self.cursor.fetchall()

        # self.cursor.execute("select crate,card,channel,nohvpmt,sequencer_bad,n20_bad,n100_bad,lowgain from pmtdb;")
        self.cursor.execute("SELECT crate,slot,channel,resistor_pulled,low_occupancy,zero_occupancy,bad_base_current FROM channel_status;")
        self.pulledPMTs= self.cursor.fetchall()

        self.cursor.execute("SELECT B.crate, A.slot, A.channel, B.hv_relay_mask1, B.hv_relay_mask2 from channel_status as A INNER JOIN  current_crate_state as B ON B.crate = A.crate;")
        self.relayMasks= self.cursor.fetchall()

        self.channelState={}
        i=0
        # print self.dic

        for crate in range(19):
            self.channelState[str(crate)]={}
            for card in range(self.numOfSlots):
                self.channelState[str(crate)][str(card)]={}
                for channel in range(self.numOfChannels):
                    self.channelState[str(crate)][str(card)][str(channel)]={}


        # Set relay status.
        for record in self.relayMasks:
            self.channelState[str(record[0])][str(record[1])][str(record[2])]["open"] = False if (record[4]<<32 | record[3]) & (1 << (record[1]*4 + (3-record[2]//8))) else True


        #This pulls in the pmt type 
        for record in self.info:
            self.channelState[str(record[0])][str(record[1])][str(record[2])]["type"] = self.pmt_type_description(record[3])

        for record in self.pulledPMTs:
            self.channelState[str(record[0])][str(record[1])][str(record[2])]["nohvpmt"] = record[3]
            self.channelState[str(record[0])][str(record[1])][str(record[2])]["lowOcc"] = record[4]
            self.channelState[str(record[0])][str(record[1])][str(record[2])]["zeroOcc"] = record[5]
            self.channelState[str(record[0])][str(record[1])][str(record[2])]["badbase"] = record[6]


    def enable_menu(self,option):
        self.crate_options["state"] = 'normal'
        self.color_Schemes["state"] = 'normal'

        #Connect to database only when an options on the dropdown is selected.

        self.crateView.itemconfigure(self.labelText,text="%s on Crate %s"%(self.poll_options_header.get(),self.crate_options_header.get()))


    def makeData(self):

        holder={} 
        for crate in range(19):
            holder[str(crate)]={}
            for card in range(self.numOfSlots):
                holder[str(crate)][str(card)]=[]
                for channel in range(self.numOfChannels):
                
                    self.newData['BASE'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
                    self.newData['BASE'][str(crate)][str(card)][str(channel)]['value']=float(np.random.rand()*1000000)
                    self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
                    self.newData['CMOS'][str(crate)][str(card)][str(channel)]['value']=float(np.random.rand()*1000000)
                    holder[str(crate)][str(card)]=np.random.rand()
                    # holder.setdefault(str(card),[]).append(np.random.rand())
        return holder

        
    def percentile(self,lis,bounds):
        return [np.sort(lis)[np.floor(len(lis)*bound/100.01)] for bound in bounds]
        


if __name__ == '__main__':

    App()

