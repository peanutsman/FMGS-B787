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

test_initialisation = ini.Test("Test de l'initialisation", 10)

def stop_ivy_bus():
    IvyStop()
    test_initialisation.x = time_x
    test_initialisation.create_test_file()

def on_msg_StateVector(agent, *data):
    global StateVector
    StateVector = data
    print(StateVector)
    test_initialisation.y.append(StateVector)
    test_initialisation.timer(stop_ivy_bus, time_x)

##########################################################################
IvyInit ("Test_init_state_vector", " Ready ", 0 , initialisation_FMS, on_die_fms)
IvyStart ("224.255.255.255:2010")
IvyBindMsg (on_msg_Time, '^Time t=(.*)')
##########################################################################

IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')

##########################################################################
IvyMainLoop()


