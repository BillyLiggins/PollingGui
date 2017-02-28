#!/usr/bin/python
import Tkinter
import Tkinter as tk
import tkMessageBox
# from snotdaq import DataStream
import time
import socket
import struct
import numpy as np
import os

# Imports for PSQL access
import psycopg2
import psycopg2.extras

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
            conn.close()
            self.destroy()
        except psycopg2.Error as e:
            tkMessageBox.showerror('Error',('Unable to connect! {0} \nMight be due to no connection to the DB or a wrong password').format(e))

