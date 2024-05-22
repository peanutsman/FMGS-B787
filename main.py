####Fichier main FMGS####

from ivy . std_api import *
import time
import math
import flight_plan as fp
import performances as perf

app_name = "FMGS"
bus_Ivy = "127.255.255.255:2010"
#bus_Ivy = "255.255.248.0.2010"
#bus_Ivy = "172.20.10.255:2087"

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
volets = '0'
landing_gear = 1
overfly = 0
flyby = 1
epsilon_overfly = 10
trans_alt = 5000
VMAXFL100 = 250
xpos = 1
ypos = 2
x = 0
y = 1
first_wpt = 0
SPDstatevector = 3
ALTstatevector = 2
type_wpt_fp = 4
v_vent =0
dir_vent = 1

flight_plan_used = fp.fptdpG
#flight_plan_used = fp.fp_test

def meters_to_feet(meters: float):
    return meters * 3.28084

def knots_to_ms(knots: float):
    return knots * 0.514444

def deg_to_rad(deg: float):
    return deg * math.pi / 180
def rad_to_deg(rad: float):
    return rad * 180 / math.pi

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
        x_premier_wpt = float(flight_plan_used[first_wpt][xpos])
        y_premier_wpt = float(flight_plan_used[first_wpt][ypos])
        xy_premier_wpt = [x_premier_wpt, y_premier_wpt]
        xy_deuxieme_wpt = [float(flight_plan_used[first_wpt+1][xpos]), float(flight_plan_used[first_wpt+1][ypos])]

        windspeed = fp.wind[v_vent]
        winddir = fp.wind[dir_vent]
        QFU = leg_cap(xy_premier_wpt, xy_deuxieme_wpt)
        xpoint=fp.V_Init*math.cos(fp.Gamma_Init)*math.cos(QFU) +windspeed*math.cos(winddir)
        ypoint=fp.V_Init*math.cos(fp.Gamma_Init)*math.sin(QFU) +windspeed*math.sin(winddir)
        print(rad_to_deg(QFU),"QFU")
        derive =math.asin(windspeed*math.sin(QFU-deg_to_rad(fp.Dir_Vent))/(knots_to_ms(fp.V_Init)*math.cos(deg_to_rad(fp.Gamma_Init))))
        print("dérive:",rad_to_deg(derive))
        cap_vent_piste = QFU -  derive
        print("cap vent piste:",rad_to_deg(cap_vent_piste))
        IvySendMsg("InitStateVector x=%s y=%s z=0.0000 Vp=100.0000 fpa=0.0000 psi=%s phi=0.0000" %(str(x_premier_wpt), str(y_premier_wpt),str(cap_vent_piste)))
    
    ###ENVOI DES PERFOS
    envoi_perfo()
    
    ###ENVOI DU VENT
    envoi_vent()

    ###ENVOI DE LA VITESSE MANAGEE
    envoi_vitesse()

    ###ENVOIE DES LEGS
    envoi_route(flight_plan_used)
    
    ####ENVOI DE L'ALTITUDE MANAGEE
    envoi_altitude(flight_plan_used)

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
    perfos = perf.perfos_avion(volets, landing_gear)
    IvySendMsg("NxMax=%s NxMin=%s NzMax=%s NzMin=%s PMax=%s AlphaMax=%s AlphaMin=%s PhiMaxManuel=%s PhiMaxAutomatique=%s GammaMax=%s GammaMin=%s MagneticDeclination=%s" %(perfos["NxMax"], perfos["NxMin"], perfos["NzMax"], perfos["NzMin"], perfos["PMax"], perfos["AlphaMax"], perfos["AlphaMin"], perfos["PhiMaxManuel"], perfos["PhiMaxAutomatique"], perfos["GammaMax"], perfos["GammaMin"], perfos["MagneticDeclination"]))

def envoi_vent():
    IvySendMsg("WindVelocity=%s WindDirection=%s" %(fp.wind[v_vent], fp.wind[dir_vent]))

def envoi_route(flight_plan :list):
    global wpt_courant
    wpt_courant = sequencement_leg(flight_plan)
    xy_wpt_courant = [float(flight_plan[wpt_courant][xpos]), float(flight_plan[wpt_courant][ypos])]
    xy_wpt_suivant = [float(flight_plan[wpt_courant+1][xpos]), float(flight_plan[wpt_courant+1][ypos])]
    envoi_leg(xy_wpt_courant, xy_wpt_suivant)

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
def envoi_leg(xy_waypoint1: list, xy_waypoint2 : list):
    cap_leg = leg_cap(xy_waypoint1, xy_waypoint2)
    IvySendMsg("LegX=%s LegY=%s LegCap=%s" %(xy_waypoint1[x],  xy_waypoint1[y], cap_leg))

#### ENVOIE  DE LA VITESSE/MACH MANAGE
def envoi_vitesse():
    alt = float(StateVector[ALTstatevector])
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
    vitesse = float(StateVector[SPDstatevector]) ##convertir en m/s la string du state vector
    rayon = vitesse**2/(g*math.atan(perf.perfos_avion(volets,landing_gear)['PhiMaxAutomatique']))
    distance_virage = rayon * math.tan(delta_cap_wpt3_wpt1/2)
    return distance_virage

#en entrée : deux liste correspondant aux coord x,y waypoint 
def leg_cap(xy_waypoint1, xy_waypoint2):
    cap_leg = math.atan2(xy_waypoint2[y]-xy_waypoint1[y],xy_waypoint2[x]-xy_waypoint1[x])
    return cap_leg

def distance_to_go(xy_waypoint1, xy_waypoint2):
    distance = math.sqrt((xy_waypoint2[x] - xy_waypoint1[x])**2 + (xy_waypoint2[y] - xy_waypoint1[y])**2)
    return distance

def sequencement_leg(flight_plan :list):
    global dirto_status, wpt_courant
    xy_avion = [float(StateVector[x]), float(StateVector[y])]
    
    ### SI FIN DE PLAN DE VOL
    if wpt_courant == len(flight_plan)-1:
        return wpt_courant
    
    ####DIR TO
    if dirto_status:
        wpt_index_after_dirto = wpt_courant+1
        xy_wpt_dirto = [float(flight_plan[wpt_courant][xpos]), float(flight_plan[wpt_courant][ypos])]
        xy_next_waypoint = [float(flight_plan[wpt_index_after_dirto][xpos]), float(flight_plan[wpt_index_after_dirto][ypos])]
        if flight_plan[wpt_courant][type_wpt_fp] == overfly:
            if distance_to_go(xy_avion, xy_wpt_dirto) < epsilon_overfly:
                dirto_status = False
                return wpt_index_after_dirto
        elif flight_plan[wpt_courant][type_wpt_fp] == flyby:
            if distance_to_go(xy_avion, xy_wpt_dirto) < 2*distance_to_end_leg(xy_avion, xy_wpt_dirto, xy_next_waypoint):
                dirto_status = False
                return wpt_index_after_dirto
        
        return wpt_courant
    
    ####SEQUENCEMENT LEGS
    for wpt in range(1, len(flight_plan)-1):
        xy_wpt=[float(flight_plan[wpt][xpos]), float(flight_plan[wpt][ypos])]
        xy_previous_wpt = [float(flight_plan[wpt-1][xpos]), float(flight_plan[wpt-1][ypos])]
        xy_wpt_suivant = [float(flight_plan[wpt+1][xpos]), float(flight_plan[wpt+1][ypos])]
        distance = distance_to_go(xy_wpt, xy_avion)
        if flight_plan[wpt][type_wpt_fp] == flyby:
            if distance < 2*distance_to_end_leg(xy_previous_wpt, xy_wpt, xy_wpt_suivant):
                return wpt #index du waypoint dans le flight plan
        elif flight_plan[wpt][type_wpt_fp] == overfly:
            if distance < epsilon_overfly:
                return wpt
    return wpt_courant ## --> dans le cas ou on continue sur le leg actuel
    ### la méthode doit aussi prendre en compte qu'après le dernier waypoint : arrêt de l'avion

def envoi_altitude(flight_plan :list):
    altitude = flight_plan[wpt_courant][type_wpt_fp]
    if altitude == fp.undefined_z:
        altitude = StateVector[ALTstatevector]
    IvySendMsg("AltManaged=%s" %altitude)
    
IvyInit (app_name, "Ready to receive", on_die, initialisation_FMS)
IvyStart (bus_Ivy)

IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')
IvyBindMsg(on_msg_time, '^Time t=(.*)')
IvyBindMsg(on_msg_dirto, '^DirTo Wpt=(.*)')
IvyBindMsg(on_msg_volets, '^VoletState=(.*)')
IvyBindMsg(on_msg_landing_gear, '^LandingGearState=(.*)')

IvyMainLoop()