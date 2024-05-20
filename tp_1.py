from ivy . std_api import *
import time

def null_cb (*a):
    pass

def on_cx_proc (agent , connected ) :
    pass
def on_die_proc (agent , _id ):
    pass

app_name = "FMGS"
ivy_bus = "127.255.255.255:2011"

IvyInit (app_name, "Ready to receive", 0, null_cb, null_cb )
IvyStart (ivy_bus)

time.sleep(1.0)

IvySendMsg("Msg1=69LATRICK" "Msg2=SigneNorman")

IvyStop