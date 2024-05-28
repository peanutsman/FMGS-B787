from ivy . std_api import *
from time import sleep

acquisition = False
volet_state = '0'

landing_gear = 0
test_volets = 1

def init_basse_altitude():
    print("Test avec altitude basse = 1000m")
    IvySendMsg("InitStateVector x=0 y=0 z=1000.0000 Vp=100 fpa=0.0000 psi=0 phi=0.0000")

def init_haute_altitude():
    print("Test avec altitude haute = 10000m")
    IvySendMsg("InitStateVector x=0 y=0 z=10000.0000 Vp=100 fpa=0.0000 psi=0 phi=0.0000")

def envoi_volets(state):
    global acquisition
    IvySendMsg("VoletState=%s"%state)
    acquisition = True

def envoyer_landing_gear(state):
    global acquisition
    IvySendMsg("LandingGearState=%s"%state)
    acquisition = True

def on_msg_facteur(agent, *perf):
    global acquisition
    if acquisition==True:
        nxmax = perf[0]
        nxmin = perf[1]
        nzmax = perf[2]
        nzmin = perf[3]
        if test_volets==1:
            print("\nLa Configuration des volets est : %s\n"%volet_state)
        else:
            print("\nLa Configuration des trains est : %s "%landing_gear)
        print("NxMax=%s NxMin=%s NzMax=%s NzMin=%s\n"%(nxmax, nxmin, nzmax, nzmin))
        acquisition = False

def test_des_volets():
    global acquisition, volet_state, test_volets
    IvySendMsg("LandingGearState=1")
    sleep(2)
    acquisition = True
    for i in range(0,4):
        volet_state = '' + str(i)
        envoi_volets(volet_state)
        sleep(3)
    test_volets = 0

def test_landing_gear():
    global acquisition, landing_gear, test_volets
    IvySendMsg("VoletState=0")
    sleep(2)
    acquisition = True
    for i in range(0,2):
        landing_gear = i
        envoyer_landing_gear(landing_gear)
        sleep(3)
    test_volets = 1



#######################################################################################################################
#Bus IVY
app_name = "Test_Performances"
bus_Ivy = "127.255.255.255:2010"
#bus_Ivy = "255.255.248.0.2010"
#bus_Ivy = "172.20.10.255:2087"
#bus_Ivy_nonoelastico = "192.168.106.255:2087"

def null(*args):
    pass


IvyInit (app_name, "Ready to receive", null, null)
IvyStart (bus_Ivy)
sleep(1)
IvyBindMsg(on_msg_facteur, "Performances NxMax=(.*) NxMin=(.*) NzMax=(.*) NzMin=(.*) PMax=(.*) PMin=(.*) AlphaMax=(.*) AlphaMin=(.*) PhiMaxManuel=(.*) PhiMaxAutomatique=(.*) GammaMax=(.*) GammaMin=(.*) Vmo=(.*) Mmo=(.*)")
init_basse_altitude()
sleep(5)
test_des_volets()
test_landing_gear()
sleep(5)
init_haute_altitude()
test_des_volets()
test_landing_gear()
IvyStop()
    

    #######################################################################################################################