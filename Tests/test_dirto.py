from ivy . std_api import *
from time import sleep

 
acquisition = False
dirtostatus = False

def onmsg_axe(a, *axe):
    global acquisition
    if acquisition == True and dirtostatus == True:
        print("La position de l'avion est x=22000 y=6000\n")
        print("L'axe entre l'avion et le waypoint est de 0°")
        print("L'axe envoyée par le FMGS en mode DIRTO est : x=%s y=%s cap=%s" %axe[0], axe[1], axe[2])
        acquisition = False
    if acquisition == True:
        print("L'axe envoyée est : x=%s y=%s cap=%s" %axe[0], axe[1], axe[2])
    
def init_test():
   global acquisition
   IvySendMsg("InitStateVector x=22000 y=6000 z=0 Vp=0.00 fpa=0.0000 psi=0 phi=0.0000")
   sleep(2)
   acquisition = True

def init_dirto():
    global acquisition, dirtostatus
    IvySendMsg("DirTo Wpt=WPTA")
    sleep(2)
    acquisition = True

#######################################################################################################################
#Bus IVY
app_name = "Test_DIRTO"
bus_Ivy = "127.255.255.255:2010"

def null(*args):
    pass


IvyInit (app_name, "Ready to receive", null, null)
IvyStart (bus_Ivy)
sleep(1)
IvyBindMsg(onmsg_axe, "AxeFlightPlan LegX=(.*) LegY=(.*) LegCap=(.%)")
init_test()
sleep(5)
init_dirto()
sleep(5)
IvyStop()
    

    #######################################################################################################################
