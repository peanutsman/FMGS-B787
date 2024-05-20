####Fichier main FMGS####

from ivy . std_api import *
import time
import math
import flight_plan as fp

app_name = "FMGS"
bus_Ivy = "127.255.255.255:2011"

def initialisation_FMS (*a):
    IvySendMsg("FMSStatus=Connected")

def on_die(*a):
    IvySendMsg("FMSStatus=Disconnected")
    IvyStop()

recorded_data = None
StateVector = None

def meters_to_feet(meters):
    return meters * 3.28084

def knots_to_ms(knots):
    return knots * 0.514444

def on_msg(agent, *data):
    global recorded_data
    recorded_data = data [0]
    print ("First arg in msg: %s" %data [0])
    IvySendMsg("Bonjour")

def on_msg_StateVector(agent, *data):
    global StateVector
    StateVector = data [0]
    print ("First arg in msg: %s" %data [0])

def envoi_leg(waypoint):
    x1 = fp.fptdpG[waypoint][1]
    y1 = fp.fptdpG[waypoint][2]
    x2 = fp.fptdpG[waypoint+1][1] ##ça va pas marcher car waypoint = nom et pas index, ou alors dans la fonction def leg_courant : renovyer l'index et pas le nom du waypoint
    y2 = fp.fptdpG[waypoint+1][2]
    cap_leg = math.atan2(y2-y1,x2-x1)
    IvySendMsg("LegX=%s" "LegY=%s" "LegCap=%s" %x1 %y1 %cap_leg)

def altitude(statevector):
    alt = statevector[2]
    if meters_to_feet(alt) < 10000:
        speed = knots_to_ms(250)
    if meters_to_feet(alt) >= 10000:
        speed = knots_to_ms(fp.cost_index_speed)     
    IvySendMsg("VcManaged=%s" %speed)



IvyInit (app_name, "Ready to receive", 0, initialisation_FMS)
IvyStart (bus_Ivy)

IvyBindMsg(on_msg_StateVector, '^StateVector=(.*)')
IvyMainLoop()