from ivy . std_api import *
from time import sleep
####AVANT DE COMMENCER LE TEST : Remplacer le flight plan used par le fp_dirto dans flight_plan.py
 
acquisition = False
dirtostatus = False
statev = None

def onmsg_statevector(a, *sv):
    global statev
    statev = sv

def onmsg_axe(a, *axe):
    global acquisition
    if acquisition == True and dirtostatus == True:
        print("La position de l'avion est x=%s y=%s" %(statev[0], statev[1]))
        print("axe =", axe)
        print("\nL'axe envoyée par le FMGS en mode DIRTO est : x=%s y=%s cap=%s" %(axe[0], axe[1], axe[2]))
        acquisition = False
    if acquisition == True:
        print("axe =", axe)
        print("L'axe envoyée est : x=%s y=%s cap=%s\n" %(axe[0], axe[1], axe[2]))
        acquisition = False
    
def init_test_flyby():
    global acquisition, dirtostatus
    IvySendMsg("InitStateVector x=6300 y=2300 z=0 Vp=10.00 fpa=0.0000 psi=0 phi=0.0000")
    sleep(2)
    acquisition = True
    dirtostatus = True
    
def init_test_overfly():
    global acquisition, dirtostatus
    IvySendMsg("InitStateVector x=4000 y=2000 z=0 Vp=10.00 fpa=0.0000 psi=0 phi=0.0000")
    sleep(2)
    acquisition = True
    dirtostatus = False

    
def init_test():
   global acquisition
   IvySendMsg("InitStateVector x=0.0 y=0.0 z=0 Vp=10.00 fpa=0.0000 psi=0 phi=0.0000")
   sleep(2)
   acquisition = True

def init_dirto():
    global acquisition, dirtostatus
    IvySendMsg("DirTo Wpt=WPTA")
    print("\nDirTo initié vers le WPTA")
    sleep(2)
    acquisition = True
    dirtostatus = True

#######################################################################################################################
#Bus IVY
app_name = "Test_DIRTO"
#bus_Ivy = "127.255.255.255:2010"
bus_Ivy = "127.255.255.255:2010"

def null(*args):
    pass


IvyInit (app_name, "Ready to receive", null, null)
IvyStart (bus_Ivy)
sleep(1)
IvyBindMsg(onmsg_statevector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')
IvyBindMsg(onmsg_axe, "AxeFlightPlan LegX=(.*) LegY=(.*) LegCap=(.*)")
init_test()
sleep(5)
init_dirto()
sleep(5)
init_test_flyby()
sleep(5)
init_test_overfly()
sleep(5)
IvyStop()
    

    #######################################################################################################################
