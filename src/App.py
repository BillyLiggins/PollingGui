#!/usr/bin/python
#import matplotlib
#matplotlib.use("TkAgg")
#
import math
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure
import random
import Tkinter
import Tkinter as tk
import ttk
import tkFont
from snotdaq import DataStream
from snotdaq.datastream import *
import time
import socket
import struct
import numpy as np
# import demo_tooltips_2
import os
import time 


# Imports for PSQL access
import psycopg2
import psycopg2.extras
import passwordDialog

#------------------------------------
# You need to make a cell manger that makes the cells and then handles the updateing.
#
#
#
#------------------------------------

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
        self.unit="k"
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
	self.unitScale={"":0,"k":3,"M":6,"T":9}


        self.rectID=self.mother.crateView.create_rectangle(x1,y1,x2,y2,fill='black')
        # self.rectID=canvas.create_rectangle(x1,y1,x2,y2,fill='black')
        self.overlayText()

    def overlayText(self):
        self.textID= self.canvas.create_text((self.x1+self.width/2,self.y1+self.height/2),text=(self.word+self.unit),fill='white',font= ("helvetica", 8))

    def updateText(self):
        if self.mother.dic[str(self.crate.get())][str(self.card)][str(self.channel)]==True:
            self.toolTipText="Card %i, Channel %i pulled resistor" % (self.card,self.channel)
        else:
            self.toolTipText="Card %i, Channel %i" % (self.card,self.channel)
        self.canvas.itemconfigure(self.textID,text=(self.word+self.unit))
        self.canvas.tag_bind(self.rectID,"<Enter>", self.enter)
        self.canvas.tag_bind(self.rectID,"<Leave>", self.leave)
        self.canvas.tag_bind(self.rectID,"<B1-Motion>",self.enter)
        self.canvas.tag_bind(self.textID,"<Enter>", self.enter)
        self.canvas.tag_bind(self.textID,"<Leave>", self.leave)
        self.canvas.tag_bind(self.textID,"<B1-Motion>",self.enter)
    
    def updateColor(self,bounds,pulledDict):
        #print "Bounds[0] = ",bounds[0]
        #print "Bounds[1] = ",bounds[1]
        textColor="black"
        if self.word =='N/A':
            self.canvas.itemconfigure(self.rectID,fill='black')
            self.canvas.itemconfigure(self.textID,fill='white')
            return
        self.mother.dropDown.itemconfigure(self.mother.text_bounds, text = "Bounds: %f to %f"%(bounds[0],bounds[1]))

        if pulledDict[str(self.crate.get())][str(self.card)][str(self.channel)]==True:
            color="gray"
        if pulledDict[str(self.crate.get())][str(self.card)][str(self.channel)]==False:
            if float(self.word)*10**self.unitScale[self.unit] < bounds[0]:
                color = self.colors[0]
                textColor = self.invertedColors[0]
            elif bounds[0] <= float(self.word)*10**self.unitScale[self.unit] < bounds[1]:
                color = self.colors[1]
                textColor = self.invertedColors[1]
            elif bounds[1]<=float(self.word)*10**self.unitScale[self.unit]:
		#print "got a red"
                color = self.colors[2]
                textColor = self.invertedColors[2]
        self.canvas.itemconfigure(self.rectID,fill=color)
        #self.canvas.itemconfigure(self.rectID,activefill="gold")
        #self.canvas.itemconfigure(self.textID,activefill='white')

        if color == "gray":
            self.canvas.itemconfigure(self.rectID,outline="black")
        else:
            self.canvas.itemconfigure(self.rectID,outline=color)

        self.canvas.itemconfigure(self.textID,fill=textColor)
        
    def enter(self, event=None):
        self.mother.dropDown.delete(self.mother.mousePosID)
        self.schedule()

        self.mother.mousePos = tk.Label(self.mother.dropDown, text = "Crate %s , Card %s , Channel %s"%(self.crate.get(),self.card,self.channel),fg = "black" ,bg="gray", width=25,height=1,font= ("helvetica", 12))
        self.mother.mousePosID=self.mother.dropDown.create_window(self.mother.cell_canvas_width/6,0.1*self.mother.cell_canvas_height,window=self.mother.mousePos)


    def leave(self, event=None):
        self.mother.dropDown.delete(self.mother.mousePosID)

        self.mother.mousePos = tk.Label(self.mother.dropDown, text = "Crate %s , Card %s , Channel %s"%("-","-","-"),fg = "black" ,bg="gray", width=25,height=1,font= ("helvetica", 12))
        self.mother.mousePosID=self.mother.dropDown.create_window(self.mother.cell_canvas_width/6,0.1*self.mother.cell_canvas_height,window=self.mother.mousePos)

        self.unschedule()
        self.hidetip()


    def schedule(self):
        self.unschedule()
        # self.id = self.widget.after(self.waittime, self.showtip)
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
        
        self.d =  passwordDialog.PasswordDialog(self.master)
        self.d.pack()
        self.master.wait_window(self.d)

        # Set up the connection to the database
        os.environ['PGOPTIONS'] = '-c statement_timeout=10000' #in ms
        self.conn = psycopg2.connect('dbname=%s user=%s password=%s host=%s connect_timeout=5 '
                                % (self.d.name, self.d.user, self.d.password, self.d.host))

         

        print "Width = ",self.cell_canvas_width
        print "height = ",self.cell_canvas_height

        self.poll_options=["Base currents","CMOS rates"]
        self.sub_opinions=["BASE","CMOS"]

        self.numOfSlots= 16
        self.numOfChannels= 32
        self.numOfCrates = 18+1
        self.millnames = ['','k','M','B','T']
	self.unitScale={"":0,"k":3,"M":6,"T":9}
        self.clearingTime=5000

        self.findChannelState()
        self.init_datastream()
        self.init_dropDown()
        self.init_crateView()
        self.init_crate()

        self.update_crates()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()

    def on_closing(self):
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                        self.master.destroy()



    def init_datastream(self):

        # self.data = DataStream('buffer1.sp.snolab.ca', name='polling_gui', subscriptions=['BASE','CMOS'])
        self.data = DataStream('192.168.80.124', name='polling_gui', subscriptions=['BASE','CMOS'])
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

    def pullData(self):
        print 'pulling data'
        self.getRecord()
        self.parseRecord()
        self.clearTime()

    def getRecord(self):
        """TODO: Docstring for pollBaseCurrents.
        :returns: TODO

        """
        print 'getRecord()'

        try:
            self.id, self.record = self.data.recv_record()
        except socket.timeout:
            time.sleep(0.01)
            self.getRecord()
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
            print 'After sleep(1)'
            self.getRecord()

            return

        #print "id = ", self.id
        #print "record= ", self.record
        #
        if self.id not in self.sub_opinions :
             #master.after(100, update_fifo_levels, master)
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
            #hack ask tony about polling one card.
            pmtCurrents=np.split(np.array(unpackedData[19:19+512])-127,16)
            busyFlags=np.array(unpackedData[19+512:])

            # print "crate = ", type(crate)
            # print "slotMask = ", self.slotMask
            # print "errorFlags = ", self.errorFlag
            # print "pmtCurrents = ",pmtCurrents[0][0]
            # print "type(pmtCurrents) = ",type(pmtCurrents[0][0])
            # print "busyFlags= ",self.busyFlags

            for card in range(16):
                # if (1<<card)&slotMask = slotMask:
                    for channel in range(32):
                        # if (1<<card)&channelMasks=channelMasks:
                                self.newData['BASE'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
                                self.newData['BASE'][str(crate)][str(card)][str(channel)]['value']=float(pmtCurrents[card][channel])
            print 'polled BASE from crate ',crate

        if self.id == 'CMOS':
        # What happens when a CMOS rate is received.

            crate, counts, errorFlag = parse_cmos_record(self.record, None) 

            if not errorFlag:
                for card in range(16):
                    if counts[card]==None:
                        # print "counts[card] = ", counts[card], " got continued"
                        continue
                    for channel in range(32):
                        # Ask whether the CMOS record has been received and successfully parsed. If so then initialise it and break.
                        if self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']==None or self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value']==None:
                            self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
                            self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value']=counts[card][channel]
                            continue

                        
                        self.newData['CMOS'][str(crate)][str(card)][str(channel)]['value']=( counts[card][channel]-self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value'] )/(time.time()-self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp'])

                        # self.newData['CMOS'][str(crate)][str(card)][str(channel)]['value']=( counts[card][channel]-self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value'] )/(time.time()-self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp'])

                        self.newData['CMOS'][str(crate)][str(card)][str(channel)]['init_value']=counts[card][channel]
                        self.newData['CMOS'][str(crate)][str(card)][str(channel)]['timestamp']=time.time()
            print 'polled CMOS from crate ',crate
        

    def init_dropDown(self):
        """TODO: Docstring for init_dropDown.

        :f: TODO
        :returns: TODO

        """
        
        self.dropDown= Tkinter.Canvas(self.master, width=self.cell_canvas_width/3, height=self.cell_canvas_height,background='gray')
        self.dropDown.grid(row=0,column=0,sticky=Tkinter.N)

        self.poll_options_header= Tkinter.StringVar(self.master)
        self.poll_options_header.set("Pick Poll") # default value

        self.text_polling = tk.Label(self.dropDown, text="Polling : ",bg = "gray" ,fg="black", width=12,height=1,font= ("helvetica", 12))
        self.dropDown.create_window((self.cell_canvas_width/6),0.2*self.cell_canvas_height-24,window=self.text_polling)

        # self.button = tk.Button(self.dropDown, text="kill",bg = "gray" ,fg="black", width=12,height=1,font= ("helvetica", 12),command=self.killPol)
        # self.dropDown.create_window((self.cell_canvas_width/6),0.15*(self.cell_canvas_height-24),window=self.button)

        # self.poll_dropdown= Tkinter.OptionMenu(self.dropDown,self.poll_options_header, *self.poll_options, command = self.enable_menu)
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
        #must be a better way to do this.
        # self.leg_lower_header= Tkinter.StringVar(self.dropDown)
        # self.leg_lower_header.set(str(self.bounds[0])+"% < x") # default value
        # self.leg_middle_header= Tkinter.StringVar(self.dropDown)
        # self.leg_middle_header.set(str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%") # default value
        # self.leg_high_header= Tkinter.StringVar(self.dropDown)
        # self.leg_high_header.set("x < "+str(self.bounds[1])+"%") # default value
        #
        # self.leg_lower= tk.Label(self.dropDown, text=self.leg_lower_header,fg = "white" ,bg="black", width=12,height=1,font= ("helvetica", 12))
        # self.leg_middle= tk.Label(self.dropDown, text=self.leg_middle_header,fg = "black" ,bg="green", width=12,height=1,font= ("helvetica", 12))
        # self.leg_high= tk.Label(self.dropDown, text=self.leg_high_header,fg = "black" ,bg="red", width=12,height=1,font= ("helvetica", 12))

        # self.leg_lower= tk.Label(self.dropDown, text=str(self.bounds[0])+"% < x",fg = "white" ,bg="black", width=12,height=1,font= ("helvetica", 12))
        # self.leg_middle= tk.Label(self.dropDown, text=str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%",fg = "black" ,bg="green", width=12,height=1,font= ("helvetica", 12))
        # self.leg_high= tk.Label(self.dropDown, text="x < "+str(self.bounds[1])+"%",fg = "black" ,bg="red", width=12,height=1,font= ("helvetica", 12))

        # self.legID1=self.dropDown.create_window(self.cell_canvas_width/6,0.5*self.cell_canvas_height,window=self.leg_lower)
        # self.legID2=self.dropDown.create_window(self.cell_canvas_width/6,0.5*self.cell_canvas_height+22,window=self.leg_middle)
        # self.legID3=self.dropDown.create_window(self.cell_canvas_width/6,0.5*self.cell_canvas_height+44,window=self.leg_high)

        self.legID1=self.dropDown.create_rectangle(self.cell_canvas_width/12,0.5*self.cell_canvas_height-10,self.cell_canvas_width*3/12,0.5*self.cell_canvas_height+10,outline="black",fill="black")
        self.legID2=self.dropDown.create_rectangle(self.cell_canvas_width/12,0.5*self.cell_canvas_height+10,self.cell_canvas_width*3/12,0.5*self.cell_canvas_height+30,outline="green",fill="green")
        self.legID3=self.dropDown.create_rectangle(self.cell_canvas_width/12,0.5*self.cell_canvas_height+30,self.cell_canvas_width*3/12,0.5*self.cell_canvas_height+50,outline="red" ,fill="red")

        self.leg_lower = self.dropDown.create_text(self.cell_canvas_width/6,0.5*self.cell_canvas_height,text=str(self.bounds[0])+"% < x", fill = "white" ,font= ("helvetica", 12))
        self.leg_middle= self.dropDown.create_text(self.cell_canvas_width/6,0.5*self.cell_canvas_height+22,text=str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%", fill = "black",font= ("helvetica", 12))
        self.leg_high  = self.dropDown.create_text(self.cell_canvas_width/6,0.5*self.cell_canvas_height+44, text="x < "+str(self.bounds[1])+"%", fill = "white" ,font= ("helvetica", 12))


	self.lowEntry = Tkinter.Entry(self.dropDown, width=5)
	self.lowEntryLabel= Tkinter.Label(self.dropDown,text="low",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
        self.dropDown.create_window(self.cell_canvas_width/12,0.57*self.cell_canvas_height+44,window=self.lowEntryLabel)
        self.LowerBoundEntryID=self.dropDown.create_window(self.cell_canvas_width/12,0.6*self.cell_canvas_height+44,window=self.lowEntry)

	self.highEntry = Tkinter.Entry(self.dropDown, width=5)
	self.highEntryLabel= Tkinter.Label(self.dropDown,text="high",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))
       	self.dropDown.create_window(3*self.cell_canvas_width/12,0.57*self.cell_canvas_height+44,window=self.highEntryLabel)
        self.UpperBoundEntryID=self.dropDown.create_window(3*self.cell_canvas_width/12,0.6*self.cell_canvas_height+44,window=self.highEntry)
        #==========crate options==========
        self.mousePos = tk.Label(self.dropDown, text="Crate ",fg = "black" ,bg="gray", width=12,height=1,font= ("helvetica", 12))

        self.mousePosID=self.dropDown.create_window(self.cell_canvas_width/6,0.1*self.cell_canvas_height,window=self.mousePos)

    def updateBounds(self):
	if self.lowEntry.get():
		print "yes"
		print self.lowEntry.get()
        # while True:
        #     try:
        #         low= float(self.lowEntry.get())
        #     except ValueError:
        #         continue
        #     else:
        #         break               

                if float(self.lowEntry.get())<float(self.bounds[1]) and float(self.lowEntry.get())<=100 and float(self.lowEntry.get())>=0:
                            self.bounds[0]=float(self.lowEntry.get())
	if self.highEntry.get():
		print "yes"
		print self.highEntry.get()
                if float(self.highEntry.get())>float(self.bounds[0]) and float(self.highEntry.get())<=100 and float(self.highEntry.get())>=0:
                     self.bounds[1]=float(self.highEntry.get())
		
	if self.lowEntry.get() or self.highEntry.get() :
		self.dropDown.itemconfigure(self.leg_lower,text=str(self.bounds[0])+"% < x")
		self.dropDown.itemconfigure(self.leg_middle,text=str(self.bounds[0])+"% < x < "+str(self.bounds[1])+"%")
		self.dropDown.itemconfigure(self.leg_high,text="x < "+str(self.bounds[1])+"%")
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
                            int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

        #return '%.1f%s'%(n / 10**(3 * millidx), self.millnames[millidx])
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
            #self.qLower,self.qUpper= self.percentile(np.array([value for key,values in self.newData.items() for value in values ]),self.bounds)
            #self.numbers=[np.random.rand() for i in range(512)]
            # self.numbers=[np.random.rand() for i in range(32*16-1)]
            self.numbers=[]
            for card in range(self.numOfSlots):
                for channel in range(self.numOfChannels):
                    if self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'] != None:
		    	num,unit = self.millify(self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'])

                        self.numbers.append(float(num)*10**self.unitScale[str(unit)])
                    else:
                        self.numbers=[np.random.rand() for i in range(512)]

            
            for card in range(self.numOfSlots):
                for channel in range(self.numOfChannels):
                    if self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'] == None:
                        self.dictOfCells[str(card)][channel].word="N/A"
                        self.dictOfCells[str(card)][channel].updateColor(self.percentile(np.array(self.numbers),self.bounds),self.dic)
                    else:
                        #print self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value']
                        self.dictOfCells[str(card)][channel].word,self.dictOfCells[str(card)][channel].unit=self.millify(self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value'])
			#print self.dictOfCells[str(card)][channel].unit
                        # self.dictOfCells[str(card)][channel].word="%.2f" % self.newData[self.poll_options_header.get()][str(self.crate_options_header.get())][str(card)][str(channel)]['value']
                        self.dictOfCells[str(card)][channel].updateColor(self.percentile(np.array(self.numbers),self.bounds),self.dic)
                    self.dictOfCells[str(card)][channel].updateText()

            #self.makePlot()

        self.pullData()
	self.updateBounds()
        # self.makeData()
        self.master.after(1000, self.update_crates)


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

    def findChannelState(self):
        """TODO: Docstring for findChannelState.
        :returns: TODO

        """
        
        self.cursor = self.conn.cursor()
        # self.cursor.execute("select crate,card,channel,pmthv from pmtdb;")
        self.cursor.execute("select crate,card,channel,pmthv from pmtdb;")
        self.pulledPMTs= self.cursor.fetchall()

        self.dic={}
        i=0
        # print self.dic
        for crate in range(19):
            self.dic[str(crate)]={}
            for card in range(16):
                self.dic[str(crate)][str(card)]={}
                for channel in range(32):
                    self.dic[str(crate)][str(card)][str(channel)]={}

        for record in self.pulledPMTs:
            self.dic[str(record[0])][str(record[1])][str(record[2])] = record[3]


    def enable_menu(self,option):
        print option
        self.crate_options["state"] = 'normal'

        print "Here"
        #Connect to database only when an options on the dropdown is selected.
        print self.poll_options_header.get()
        print self.poll_options

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

    def getData(self):
        #THIS ISN'T USED
    # Template: You want a object that connects to the datasever, then sets
    # up its subscriptions, makes a dictionary of all data collected for the
    # whole dectctor with time stampes then returns that dict.

        self.newData={} 
        try: 
            for card in range(self.numOfSlots):
                for channel in range(self.numOfChannels):
                    #print self.poll.pollingDict[str(self.crate_options_header.get())][str(card)][str(channel)]['sub'] 
                    self.newData.setdefault(str(card),[]).append(self.poll.pollingDict[str(self.crate_options_header.get())][str(card)][str(channel)]['sub'])    
        except KeyError: 
            print "didn't get index"
                    
            #for card in range(self.numOfSlots):
            #    for channel in range(self.numOfChannels):
            #        
            #        self.newData.setdefault(str(card),[]).append(0)    
            return
        
    def percentile(self,lis,bounds):
        return [np.sort(lis)[np.floor(len(lis)*bound/100)] for bound in bounds]
        




if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="display fec fifo levels")
    parser.add_argument('hostname', nargs='?', default='buffer1.sp.snolab.ca')
    args = parser.parse_args()

    App()

