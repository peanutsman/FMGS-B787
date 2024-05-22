####Fichier main FMGS####

from ivy . std_api import *
import time
import math
import flight_plan as fp
import performances as perf

app_name = "FMGS"
bus_Ivy = "127.255.255.255:2010"

def initialisation_FMS (*a):
    IvySendMsg("FGSStatus=Connected")

def on_die(*a):
    IvySendMsg("FGSStatus=Disconnected")
    IvyStop()

recorded_data = None
StateVector = None
g = 9.81
dirto_status = False
wpt_courant = 0
volets = 0
landing_gear = 1
overfly = 0
flyby = 1
epsilon_overfly = 10
trans_alt = 5000
trans_fl = 50
VMAXFL100 = 250

#flight_plan_used = fp.fptdpG
flight_plan_used = fp.fp_test

def meters_to_feet(meters: float):
    return meters * 3.28084

def knots_to_ms(knots: float):
    return knots * 0.514444

def deg_to_rad(deg: float):
    return deg * math.pi / 180

phi_max = deg_to_rad(30)

def on_msg(agent, *data):
    global recorded_data
    recorded_data = data [0]
    print ("First arg in msg: %s" %data [0])
    IvySendMsg("Bonjour")

def on_msg_StateVector(agent, *data):
    #data est un tuple de nombre d'arguments variable (*)
    global StateVector
    StateVector = data #il va surement falloit récupérer les données intéressantes du string de state vector et les mettre dans une liste globale (StateVector) --> on a besoin de x,y,z,Vp 
    print("La coordonée x est : %s\n" %data[0])
    print("La coordonée y est : %s\n" %data[1])
    print("La coordonée z est : %s\n" %data[2])
    print("La vitesse est : %s\n" %data[3])
    IvySendMsg("acquisition state vector par FGS")

def on_msg_time(agent, *data):
    global dirto_status
    ###INITIALISATION DU STATEVECTOR
    if data[0] == "1.00":
        xy_premier_wpt = [float(flight_plan_used[0][1]), float(flight_plan_used[0][2])]
        xy_deuxieme_wpt = [float(flight_plan_used[1][1]), float(flight_plan_used[1][2])]
        IvySendMsg("StateVector x=%s y=%s z=0.0000 Vp=100.0000 fpa=0.0000 psi=%s phi=0.0000" %(str(flight_plan_used[0][1]), str(flight_plan_used[0][2]),str(leg_cap(xy_premier_wpt, xy_deuxieme_wpt))))
    
    ###ENVOI DES PERFOS
    envoi_perfo()
    
    ###ENVOI DE LA VITESSE MANAGEE
    envoi_vitesse()

    ###ENVOIE DES LEGS
    envoi_route(flight_plan_used)
    
    ####ENVOI DE L'ALTITUDE MANAGEE
    envoi_altitude(flight_plan_used)
    '''
    index_wpt1 = sequencement_leg(flight_plan_used)
    xy_wpt1 = [flight_plan_used[index_wpt1][1], flight_plan_used[index_wpt1][2]]
    xy_wpt2 = [flight_plan_used[index_wpt1+1][1], flight_plan_used[index_wpt1+1][2]]
    if dirto_status:
        pass
    else:
        envoi_leg(xy_wpt1, xy_wpt2)
    #####
    '''

def on_msg_volets(agent, *statut_volet):
    global volets
    volets = statut_volet[0]

def on_msg_landing_gear(agent, *statut_landing_gear):
    global landing_gear
    landing_gear = statut_landing_gear[0]

#en entrée : wpt = [nom_waypoint]
def on_msg_dirto(agent, *wpt: tuple):
    global dirto_status, wpt_courant
    dirto_status = True
    wpt_courant = fp.find_waypoint_index_in_fp(wpt[0], flight_plan_used)

def envoi_perfo():
    perfos = perf.perfos_avion(StateVector, volets, landing_gear)
    IvySendMsg("NxMax=%s NxMin=%s NzMax=%s NzMin=%s PMax=%s AlphaMax=%s AlphaMin=%s PhiMaxManuel=%s PhiMaxAutomatique=%s GammaMax=%s GammaMin=%s MagneticDeclination=%s" %(perfos["NxMax"], perfos["NxMin"], perfos["NzMax"], perfos["NzMin"], perfos["PMax"], perfos["AlphaMax"], perfos["AlphaMin"], perfos["PhiMaxManuel"], perfos["PhiMaxAutomatique"], perfos["GammaMax"], perfos["GammaMin"], perfos["MagneticDeclination"]))

def envoi_route(flight_plan :list):
    global wpt_courant
    wpt_courant = sequencement_leg(flight_plan)
    xy_wpt_courant = [float(flight_plan[wpt_courant][1]), float(flight_plan[wpt_courant][2])]
    xy_wpt_suivant = [float(flight_plan[wpt_courant+1][1]), float(flight_plan[wpt_courant+1][2])]
    envoi_leg(xy_wpt_courant, xy_wpt_suivant)

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
def envoi_leg(xy_waypoint1: list, xy_waypoint2 : list):
    cap_leg = leg_cap(xy_waypoint1, xy_waypoint2)
    IvySendMsg("LegX=%s LegY=%s LegCap=%s" %(xy_waypoint1[0],  xy_waypoint1[1], cap_leg))

#### ENVOIE  DE LA VITESSE/MACH MANAGE
def envoi_vitesse():
    alt = float(StateVector[2])
    ###CAS ou altitude sous la trans alt
    if alt in range(0,trans_alt):
        speed = knots_to_ms(fp.cost_index_ias())
        if speed > VMAXFL100:
            speed = knots_to_ms(VMAXFL100)
        IvySendMsg("VcManaged=%s" %speed)
    ###CAS ou altitude au dessus de la trans alt
    if alt > 5000:
        mach = fp.cost_index_mach()
        if alt < 10000 and (fp.mach_to_speed(mach) > VMAXFL100):
            mach = fp.speed_to_mach(VMAXFL100)
        IvySendMsg("MachManaged=%s" %mach)

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
def distance_to_end_leg(xy_waypoint1, xy_waypoint2, xy_waypoint3):
    delta_cap_wpt3_wpt1 = leg_cap(xy_waypoint2, xy_waypoint3) - leg_cap(xy_waypoint1, xy_waypoint2)
    vitesse = float(StateVector[3]) ##convertir en m/s la string du state vector
    rayon = vitesse**2/(g*math.atan(phi_max))
    distance_virage = rayon * math.tan(delta_cap_wpt3_wpt1/2)
    return distance_virage

#en entrée : deux liste correspondant aux coord x,y waypoint 
def leg_cap(xy_waypoint1, xy_waypoint2):
    cap_leg = math.atan2(xy_waypoint2[1]-xy_waypoint1[1],xy_waypoint2[0]-xy_waypoint1[0])
    return cap_leg

def distance_to_go(xy_waypoint1, xy_waypoint2):
    distance = math.sqrt((xy_waypoint2[0] - xy_waypoint1[0])**2 + (xy_waypoint2[1] - xy_waypoint1[1])**2)
    return distance

def sequencement_leg(flight_plan :list):
    global dirto_status, wpt_courant
    xy_avion = [float(StateVector[0]), float(StateVector[1])]
    
    ### SI FIN DE PLAN DE VOL
    if wpt_courant == len(flight_plan)-1:
        return wpt_courant
    
    ####DIR TO
    if dirto_status:
        wpt_index_after_dirto = wpt_courant+1
        xy_wpt_dirto = [float(flight_plan[wpt_courant][1]), float(flight_plan[wpt_courant][2])]
        xy_next_waypoint = [float(flight_plan[wpt_index_after_dirto][1]), float(flight_plan[wpt_index_after_dirto][2])]
        if flight_plan[wpt_courant][4] == overfly:
            if distance_to_go(xy_avion, xy_wpt_dirto) < epsilon_overfly:
                dirto_status = False
                return wpt_index_after_dirto
        elif flight_plan[wpt_courant][4] == flyby:
            if distance_to_go(xy_avion, xy_wpt_dirto) < 2*distance_to_end_leg(xy_avion, xy_wpt_dirto, xy_next_waypoint):
                dirto_status = False
                return wpt_index_after_dirto
        
        return wpt_courant
    
    ####SEQUENCEMENT LEGS
    for wpt in range(1, len(flight_plan)-1):
        xy_wpt=[float(flight_plan[wpt][1]), float(flight_plan[wpt][2])]
        xy_previous_wpt = [float(flight_plan[wpt-1][1]), float(flight_plan[wpt-1][2])]
        xy_wpt_suivant = [float(flight_plan[wpt+1][1]), float(flight_plan[wpt+1][2])]
        distance = distance_to_go(xy_wpt, xy_avion)
        if distance < 2*distance_to_end_leg(xy_previous_wpt, xy_wpt, xy_wpt_suivant):
            return wpt #index du waypoint dans le flight plan 
    return wpt_courant ## --> dans le cas ou on continue sur le leg actuel
    ### la méthode doit aussi prendre en compte qu'après le dernier waypoint : arrêt de l'avion

def envoi_altitude(flight_plan :list):
    global wpt_courant
    alt = float(StateVector[3])
    pass
    
IvyInit (app_name, "Ready to receive", 0, initialisation_FMS)
IvyStart (bus_Ivy)

IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')
IvyBindMsg(on_msg_time, '^Time t=(.*)')
IvyBindMsg(on_msg_dirto, '^DirTo Wpt=(.*)')
IvyBindMsg(on_msg_volets, '^VoletState=(.*)')
IvyBindMsg(on_msg_landing_gear, '^LandingGearState=(.*)')

IvyMainLoop()