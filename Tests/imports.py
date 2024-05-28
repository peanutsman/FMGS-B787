import init_test as ini
import conversion as c
from ivy . std_api import *
import math
from scipy.constants import g
import sys

time_x = []

def initialisation_FMS (*a):
    IvySendMsg("FGS_test_Status=Connected")

def on_die_fms(*a):
    IvySendMsg("FGS_test_Status=Disconnected")
    IvyStop()

def on_msg_Time(agent, *data):
    global t
    t = float(data[0])
    time_x.append(t)

##########################################################################



##########################################################################
IvyInit (" Test_init_state_vector", " Ready ", 0 , initialisation_FMS, on_die_fms)
IvyStart (" 127.255.255.255:2010 ")
IvyBindMsg (on_msg_Time, '^Time t=(.*)')
##########################################################################



##########################################################################
IvyMainLoop()