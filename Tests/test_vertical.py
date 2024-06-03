import init_test as ini
import conversion as c
from ivy.std_api import *
import math
from scipy.constants import g
import sys
import matplotlib.pyplot as plt

SUCCESS = 1
NOMBRE_DE_CAS = 0
FLIGHTPLAN_PATH = "local_flightplan.py"
time = []
counter = 0
ZcM_list = []

def initialisation_FMS (*a):
    IvySendMsg("FGS_test_Status=Connected")

def on_die_fms(*a):
    IvySendMsg("FGS_test_Status=Disconnected")
    IvyStop()

def on_msg_Time(agent, *data):
    global t
    t = float(data[0])
    time.append(t)

##########################################################################

def plt_flightplan(flightplan):
    fp = flightplan
    for waypoint in fp:
        if waypoint.z != "UNDEFINED":
            if float(waypoint.z) >= 0:
                plt.plot(waypoint.x, waypoint.y, marker='D', color='blue')
                plt.annotate(f"{waypoint.z}m", (waypoint.x, waypoint.y))
            else:
                plt.plot(waypoint.x, waypoint.y, marker='D', color='black')
                plt.annotate("Zc négative", (waypoint.x, waypoint.y))
        else:
            plt.plot(waypoint.x, waypoint.y, marker='D', color='black')
            plt.annotate("Zc non définie", (waypoint.x, waypoint.y))
    for i in range(len(fp)):
        if i+1 < len(fp):
            plt.plot((fp[i].x, fp[i+1].x), (fp[i].y, fp[i+1].y), color="red") #on crée artificiellement les legs
        else:
            plt.plot((fp[i].x, fp[0].x), (fp[i].y, fp[0].y), color="red") #on reboucle au niveau du flightplan

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Test des consignes d'altitude")

def on_msg_ZcManaged(agent, *data):
    global ZcM
    ZcM = float(data[0])
    ZcM_list.append(ZcM)
    
def vertical(position_avion):
    IvyBindMsg(on_msg_ZcManaged, '^ZcManaged=(.*)')
    plt.plot(position_avion.x, position_avion.y, marker="+", label="Position à l'envoi du SV")
    index = len(ZcM_list)
    current_ZcM = ZcM_list[index]
    plt.annotate(f"Zc = {current_ZcM}m", (position_avion.x, position_avion.y))
    IvySendMsg("InitStateVector x=%s y=%s z=0 Vp=%s fpa=0.0000 psi=0 phi=0.0000" %(str(position_avion.x), str(position_avion.y), str(c.knots_to_ms(c.ias_to_tas(100, 0)))))

def on_msg_StateVector(agent, *data):
    global StateVector
    global counter
    StateVector = data
    print(counter)
    if counter == 0:
        flightplan = ini.get_flightplan(FLIGHTPLAN_PATH)
        plt_flightplan(flightplan)
        coeff_temp = 2072/4070
        ordo_orig_temp = 0
        x_temp = 1000
        y_temp = x_temp*coeff_temp + ordo_orig_temp
        position_avion = ini.Point2D(x_temp, y_temp)
        vertical(position_avion)
        counter += 1
        print(counter)
    if counter == 1:
        coeff_temp = (-2383-2072)/(6338-4070)
        ordo_orig_temp = 10057.41
        x_temp = 5000
        y_temp = x_temp*coeff_temp + ordo_orig_temp
        position_avion = ini.Point2D(x_temp, y_temp)
        vertical(position_avion)
        counter += 1
        print(counter)
    if counter == 2:
        position_avion = ini.Point2D(6338, -2383)
        vertical(position_avion)
        counter += 1
    if counter == 3:
        coeff_temp = (-8993+2383)/(-6642-6338)
        ordo_orig_temp = -5606.442
        x_temp = 1000
        y_temp = x_temp*coeff_temp + ordo_orig_temp
        position_avion = ini.Point2D(x_temp, y_temp)
        vertical(position_avion)
        counter += 1
        print(counter)
    if counter == 4:
        coeff_temp = 8993/6642
        ordo_orig_temp = 0
        x_temp = -3000
        y_temp = x_temp*coeff_temp + ordo_orig_temp
        position_avion = ini.Point2D(x_temp, y_temp)
        vertical(position_avion)
        counter += 1
        print(counter)
    if counter == 5:
        stop_ivy_bus()
        plt.show()

def stop_ivy_bus():
    IvyStop()

test_vertical = ini.Test("Test des consignes d'altitude", -1)

##########################################################################
IvyInit ("Test_Zc", " Ready ", 0 , initialisation_FMS, on_die_fms)
IvyStart ("127.255.255.255:2010")
IvyBindMsg (on_msg_Time, '^Time t=(.*)')
##########################################################################

IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')

##########################################################################
IvyMainLoop()