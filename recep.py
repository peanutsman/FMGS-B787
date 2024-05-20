from ivy.std_api import *
import time


app_name = "FMGS"


def null_cb (*a):
    pass



recorded_data = None
def null_cb (*a):
    pass

def on_msg(agent, *data):
    global recorded_data
    recorded_data = data [0]
    print ("First arg in msg: %s" %data [0])
    IvySendMsg("Bonjour")


IvyInit (app_name, "Ready to receive", 0, null_cb, null_cb )
IvyStart ("127.255.255.255:2011")
IvyBindMsg(on_msg, '^Msg1=(.*)')
IvyMainLoop()
