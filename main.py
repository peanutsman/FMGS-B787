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
g = 9.81

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

def on_msg_time(agent, *data):
    global id_time
    if data[0] == "1.00":
        IvySendMsg("StateVector x=%s y=%s z=0.0000 Vp=100.0000 fpa=0.0000 psi=%s phi=0.0000" %leg_cap(fp.Seuil1, fp.Seuil2) %fp.Seuil1[1] %fp.Seuil1[2])
        IvyUnBindMsg(id_time)

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
def envoi_leg(waypoint1: list, waypoint2 : list):
    cap_leg = leg_cap(waypoint1, waypoint2)
    IvySendMsg("LegX=%s" "LegY=%s" "LegCap=%s" %waypoint1[1] %waypoint1[2] %cap_leg)

def altitude(statevector :list):
    alt = statevector[2]
    if meters_to_feet(alt) < 10000:
        speed = knots_to_ms(250)
    if meters_to_feet(alt) >= 10000:
        speed = knots_to_ms(fp.cost_index_speed)     
    IvySendMsg("VcManaged=%s" %speed)


#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
def distance_to_end_leg(statevector : list, waypoint1:list, waypoint2:list, waypoint3:list):
    delta_cap_wpt3_wpt1 = leg_cap(waypoint2, waypoint3) - leg_cap(waypoint1, waypoint2)
    vitesse = float(statevector[3]) ##convertir en m/s la string du state vector
    rayon = vitesse**2/(g*math.atan(phi_max))
    distance_virage = rayon * math.tan(delta_cap_wpt3_wpt1/2)
    
    return distance_virage

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby])   
def leg_cap(waypoint1: list,  waypoint2: list):
    cap_leg = math.atan2(waypoint2[2]-waypoint1[2],waypoint2[1]-waypoint1[1])
    return cap_leg

def sequencement_leg(statevector: list, fligh_plan :list):
    ###On suppose que le premier waypoint est le point de départ
    ###écrire ici le code qui permet le choix des waypoints à séquencer en fonction de la position courante
    longueur_leg = math.sqrt((waypoint2[1] - waypoint1[1])**2 + (waypoint2[2] - waypoint1[2])**2)
    #exemple de longueur d'un leg en fonction des 2 waypoints
    pass
    ### la méthode doit aussi prendre en compte qu'après le dernier waypoint : arrêt de l'avion
    #on peut aussir renvoyer l'index de la liste flight_plan qui correspond au waypoint 
    
IvyInit (app_name, "Ready to receive", 0, initialisation_FMS)
IvyStart (bus_Ivy)

IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*)')
id_time = IvyBindMsg(on_msg_time, '^Time t=(.*)')
IvyMainLoop()