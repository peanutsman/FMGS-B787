from ivy . std_api import *
from time import sleep

acquisition = False


def init_basse_altitude():
    print("Test avec altitude basse = 1000m (Transition Altitude :1666m)")
    IvySendMsg("InitStateVector x=0 y=0 z=1000.0 Vp=100 fpa=0.0000 psi=0 phi=0.0000")

def init_haute_altitude():
    print("Test avec altitude haute = 10000m (Transition Altitude :1666m)")
    IvySendMsg("InitStateVector x=0 y=0 z=10000.0000 Vp=100 fpa=0.0000 psi=0 phi=0.0000")

def on_msg_vitesse(agent, *speed):
    global acquisition
    if acquisition==True:
        statut = speed[0]
        ias = speed[2]
        mach = speed[1]
        print("\nStatut : %s et Vc=%s MachManaged=%s\n"%(statut, ias, mach))
        acquisition = False

#######################################################################################################################
#Bus IVY
app_name = "Test_Vitesse"
bus_Ivy = "127.255.255.255:2010"
#bus_Ivy = "255.255.248.0.2010"
#bus_Ivy = "172.20.10.255:2087"
#bus_Ivy_nonoelastico = "192.168.106.255:2087"

def null(*args):
    pass

IvyInit (app_name, "Ready to receive", null, null)
IvyStart (bus_Ivy)
sleep(1)
IvyBindMsg(on_msg_vitesse, "Statut=(.*) MachManaged=(.*) VcManaged=(.*)")
init_basse_altitude()
sleep(5)
acquisition = True
sleep(4)
init_haute_altitude()
sleep(2)
acquisition = True
sleep(2)
IvyStop()
    

    #######################################################################################################################