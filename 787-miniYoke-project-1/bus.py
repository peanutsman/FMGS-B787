from ivy.std_api import *

def on_cx_proc(agent, connected):
    print("Agent {} is {}connected".format(agent, "" if connected else "dis"))

def on_die_proc(agent):
    print("Agent {} has died".format(agent))

class AviBus :
    def __init__(self, appName, adress):
        self.adress = adress
        self.appName = appName
        #global = "127.255.255.255:2010" local = "127.0.0.1:8000"

        IvyInit(self.appName, "hello, world !", 0, on_cx_proc, on_die_proc)
        IvyStart(self.adress)

    def sendMsg(self, msg):
        IvySendMsg(msg)
    
    def bindMsg(self, callback, regex):
        IvyBindMsg(callback, regex)
    
    def stop(self):
        IvyStop()