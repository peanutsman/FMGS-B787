####Fichier main FMGS####
#Import des fichiers FMGS 
import flight_plan as fp
import performances as perf
import conversion as c
#Import des librairies
from ivy . std_api import *
import math
from scipy.constants import g
import sys
from PyQt5.QtWidgets import QApplication
from ivy.std_api import *
from mainwindow import MainView
import ressources_rc

#Index des paramètres des waypoint dans le flight plan
NOMWPT_FP, X_FP, Y_FP, TYPE_WPT_FP = 0, 1, 2, 3
#Index des éléments du state vector
X_SV, Y_SV, ALT_SV, SPD_SV = 0, 1, 2, 3
#Index du waypoint dans le flight plan
FIRST_WPT = 0
#Index des données de vent
V_VENT, DIR_VENT = 0, 1
#Initialisation des variables globales
t_minus_1 = 0
StateVector, volets, landing_gear = [0, 0, 0, 0, 0, 0, 0], '0', 1
dirto_status = False
offset_status, offset_dist, offset_side = None, None, None
epsilon_overfly = 200.0
declinaison = perf.perfos_avion(volets,landing_gear)['MagneticDeclination']
flight_plan_used, wpt_courant = fp.flight_plan, 0
#Constantes
FACTEUR = 2 #facteur de sécurité pour le epsilon_overfly 
OVERFLY, FLYBY = 0, 1
TRANS_ALT_FT = int(fp.trans_alt)
IASMAXFL100, FL100_FT = fp.VMAXFL100, 10000


def on_msg(agent, *data):
    try:
        pos = int(data[0]) #conversion de la position en entier
        main_view.signal_update_posi.emit(pos) #emit signal
    except ValueError:
        print(f"Invalid position received: {data[0]}")

def sur_msg(agent, *data):
    try:
        pos = int(data[0])
        main_view.signal_update_train.emit(pos)
    except ValueError:
        print(f"Invalid position received: {data[0]}")
    

#en entrée : state vector sur le bus IVY
#en sortie : acquisition du statevector en variable globale
def on_msg_StateVector(agent, *data :tuple):
    global StateVector
    StateVector = data #il va surement falloit récupérer les données intéressantes du string de state vector et les mettre dans une liste globale (StateVector) --> on a besoin de x,y,z,Vp 

#en entrée : temps sur le bus IVY
#en sortie : initialisation du state vector et envoi des perfos, du vent, de la vitesse, de la route et de l'altitude
def on_msg_time(agent, *data):
    ###INITIALISATION DE LA SIMULATION
    if data[0] == "1.00":
        init_simulation()
    ####MAJ DE L'EPSILON OVERFLY
    maj_epsilon_overfly(float(data[0]))
    ###ENVOI DES PERFOS
    envoi_perfo()
    ###ENVOI DE LA VITESSE MANAGEE
    envoi_vitesse()
    ###ENVOIE DES LEGS
    envoi_leg(flight_plan_used)
    ####ENVOI DE L'ALTITUDE MANAGEE
    envoi_altitude(flight_plan_used)

#en entrée : statut des volets sur le bus IVY
#en sortie : changement du statut des volets (variable globale)
def on_msg_volets(agent, *statut_volet):
    global volets
    volets = statut_volet[0]

#en entrée : statut du train d'atterrissage sur le bus IVY
#en sortie : changement du statut du train d'atterrissage (variable globale)
def on_msg_landing_gear(agent, *statut_landing_gear):
    global landing_gear
    landing_gear = statut_landing_gear[0]

#en entrée : wpt = [nom_waypoint]
#en sortie : changement du WPT séquencé (variable globale)
def on_msg_dirto(agent, *wpt: tuple):
    global dirto_status, wpt_courant
    dirto_status = True
    #print(wpt[0])
    wpt_courant = fp.find_waypoint_index_in_fp(wpt[0], flight_plan_used)
    print("Waypoint séquencé par le DIRTO: ", flight_plan_used[wpt_courant][NOMWPT_FP],"\n")

#en entrée : offset = [distance, side]
#en sortie : changement du statut de l'offset (variable globale)
def on_msg_offset(agent, *offset: tuple):
    global offset_status, offset_dist, offset_side
    if float(offset[0]) > 0 and offset[1] in ["L", "R"]:
        offset_status = True
        offset_dist = c.nm_to_m(float(offset[0]))
        offset_side = offset[1]
        print("Offset activé: ", offset[0], "NM ", offset_side)
    else:
        offset_status = False

#en entrée : N/A
#en sortie : envoi state vector, envoi vent, envoit déclinaison magnétique
def init_simulation():
    ###ENVOI DU STATE VECTOR
    envoi_state_vector()
    ###ENVOI DU VENT
    envoi_vent()
    ###ENVOIE DE LA DECLINAISON MAGNETIQUE
    envoi_declinaison()
#en entrée : N/A
#en sortie : envoi du state vector initial sur le bus IVY
def envoi_state_vector():
    x_premier_wpt = float(flight_plan_used[FIRST_WPT][X_FP])
    y_premier_wpt = float(flight_plan_used[FIRST_WPT][Y_FP])
    xy_premier_wpt = [x_premier_wpt, y_premier_wpt]
    xy_deuxieme_wpt = [float(flight_plan_used[FIRST_WPT+1][X_FP]), float(flight_plan_used[FIRST_WPT+1][Y_FP])]
    windspeed = fp.wind[V_VENT]
    QFU = axe_cap(xy_premier_wpt, xy_deuxieme_wpt)
    #print("QFU: GEO",c.rad_to_deg(QFU))
    #print(c.rad_to_deg(QFU),"QFU")
    derive =math.asin(windspeed*math.sin(QFU-c.deg_to_rad(fp.Dir_Vent))/(c.knots_to_ms(fp.V_Init)*math.cos(c.deg_to_rad(fp.Gamma_Init))))
    #print("dérive:",c.rad_to_deg(derive))
    cap_vent_piste = QFU -  derive 
    #print("cap vent piste:",c.rad_to_deg(cap_vent_piste))
    Z0 = c.feet_to_meters(fp.Z_Init)
    V0 = c.knots_to_ms(c.ias_to_tas(fp.V_Init, fp.Z_Init))
    IvySendMsg("InitStateVector x=%s y=%s z=0.0000 Vp=%s fpa=0.0000 psi=%s phi=0.0000" %(str(x_premier_wpt), str(y_premier_wpt), V0, str(cap_vent_piste)))
#en entrée : N/A
#en sortie : envoi du vent sur le bus IVY
def envoi_vent():
    IvySendMsg("WindComponent WindVelocity=%s WindDirection=%s" %(fp.wind[V_VENT], fp.wind[DIR_VENT]))
#en entrée : N/A
#en sortie : envoi de la déclinaison magnétique sur le bus IVY
def envoi_declinaison():
    IvySendMsg("MagneticDeclination=%s" %declinaison)

#en entrée : temps actuel sur le bus IVY
#en sortie : màj du epsilon overfly et du t_minus_1
def maj_epsilon_overfly(t):
    global t_minus_1
    global epsilon_overfly
    v = float(StateVector[SPD_SV])
    delta = t - t_minus_1
    if delta > 0:
        epsilon_overfly = FACTEUR*v*(delta)
    t_minus_1 = t

#en entrée : N/A
#en sortie : envoi des performances de l'avion sur le bus IVY
def envoi_perfo():
    perfos = perf.perfos_avion(volets, landing_gear)
    IvySendMsg("Performances NxMax=%s NxMin=%s NzMax=%s NzMin=%s PMax=%s PMin=%s AlphaMax=%s AlphaMin=%s PhiMaxManuel=%s PhiMaxAutomatique=%s GammaMax=%s GammaMin=%s Vmo=%s Mmo=%s" %(perfos["NxMax"], perfos["NxMin"], perfos["NzMax"], perfos["NzMin"], perfos["PMax"], perfos["PMin"], perfos["AlphaMax"], perfos["AlphaMin"], perfos["PhiMaxManuel"], perfos["PhiMaxAutomatique"], perfos["GammaMax"], perfos["GammaMin"], perfos["VMO"], perfos["MMO"]))

#en entrée : N/A
#en sortie : envoi de la vitesse/mach managée sur le bus IVY
def envoi_vitesse():
    alt = c.meters_to_feet(float(StateVector[ALT_SV]))
    ###IAS ou altitude sous la trans alt
    if alt in range(0,TRANS_ALT_FT):
        ias = fp.cost_index_ias()
        if ias > IASMAXFL100 and alt < FL100_FT:
            ias = c.knots_to_ms(IASMAXFL100)
        else:
            ias = c.knots_to_ms(ias)
        IvySendMsg("VcManaged=%s" %ias)
    ###CAS ou altitude au dessus de la trans alt
    if alt > TRANS_ALT_FT:
        mach = fp.cost_index_mach()
        if alt < FL100_FT and c.mach_to_tas(mach) > c.ias_to_tas(IASMAXFL100,alt):
            mach = c.tas_to_mach(c.ias_to_tas(IASMAXFL100, alt))
        IvySendMsg("MachManaged=%s" %mach)

#en entrée : flight plan (liste de waypoints, type,altitude)
#en sortie : envoi de l'altitude managée du wpt du début de leg sur le bus IVY
def envoi_altitude(flight_plan :list):
    altitude = flight_plan[wpt_courant][TYPE_WPT_FP]
    if altitude == fp.UNDEFINED_Z:
        altitude = StateVector[ALT_SV]
    IvySendMsg("ZcManaged=%s" %altitude)

#en entrée : x,y de deux waypoints
#en sortie : envoi des coordonnées du waypoint de départ et du cap du leg sur le bus IVY
def envoi_axe(xy_waypoint1: list, xy_waypoint2 : list):
    xy_avion = [float(StateVector[X_SV]), float(StateVector[Y_SV])]
    #print("distance entre les deux wpt:",distance_to_go(xy_avion, xy_waypoint2))
    cap_axe = axe_cap(xy_waypoint1, xy_waypoint2)
    IvySendMsg("AxeFlightPlan LegX=%s LegY=%s LegCap=%s" %(xy_waypoint1[X_SV],  xy_waypoint1[Y_SV], cap_axe))
    IvySendMsg("InitStateVector x=%s y=%s z=0.0000 Vp=%s fpa=0.0000 psi=%s phi=0.0000" %(StateVector[X_SV], StateVector[Y_SV], c.knots_to_ms(c.ias_to_tas(fp.V_Init,0)),cap_axe))

#en entrée : flight plan (liste de waypoints, type,altitude)
#en sortie : changement du WPT séquencé (variable globale)
def envoi_leg(flight_plan :list):
    global wpt_courant
    #print("début séquencement\n")
    wpt_courant = sequencement_leg(flight_plan)
    #print("fin séquencement\n")
    #print("\n\nWaypoint séquencé: ", flight_plan_used[wpt_courant][nomwpt],"\n")
    if offset_status and dirto_status == False:
        xy_wpt_courant = xy_offset(float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP]))
        print("Nouvelle position du wpt séquencé: ",xy_wpt_courant)
    else:
        xy_wpt_courant = [float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP])]
    xy_avion = [float(StateVector[X_SV]), float(StateVector[Y_SV])]
    #print("index du wpt séquencé: ",wpt_courant)
    #print("len de fp -1 :",len(flight_plan)-1)
    if dirto_status or wpt_courant == len(flight_plan)-1:
        envoi_axe(xy_avion, xy_wpt_courant)
    else:
        #print("ici")
        if offset_status and dirto_status == False:
            xy_wpt_suivant = xy_offset(float(flight_plan[wpt_courant+1][X_FP]), float(flight_plan[wpt_courant+1][Y_FP]))
            print("Nouvelle position du wpt suivant: ",xy_wpt_suivant)
        else:
            xy_wpt_suivant = [float(flight_plan[wpt_courant+1][X_FP]), float(flight_plan[wpt_courant+1][Y_FP])]
        envoi_axe(xy_wpt_courant, xy_wpt_suivant)

#en entrée : flight plan (liste de waypoints, type,altitude)
#en sortie : index du waypoint à séquencer en fonction des angles de virage et de la position avion
def sequencement_leg(flight_plan :list[list]):
    global dirto_status, wpt_courant
    xy_avion = [float(StateVector[X_SV]), float(StateVector[Y_SV])]
    ###SI dernier leg OU si Wpt_courant = le dernier WPT du PDV --> envoi du dernier leg
    if wpt_courant == len(flight_plan)-1:
        print("\nFin du plan de vol\n")
        return wpt_courant
    if dirto_status == False and wpt_courant == len(flight_plan)-2:
        print("\nFin du plan de vol (avant dernier waypoint)\n")
        return wpt_courant
    ####DIR TO
    #print("dirto status:\n",dirto_status)
    if dirto_status:
        wpt_index_after_dirto = wpt_courant+1
        xy_wpt_dirto = [float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP])]
        xy_next_waypoint = [float(flight_plan[wpt_index_after_dirto][X_FP]), float(flight_plan[wpt_index_after_dirto][Y_FP])]
        if flight_plan[wpt_courant][TYPE_WPT_FP] == OVERFLY:
            if distance_to_go(xy_avion, xy_wpt_dirto) < epsilon_overfly:
                dirto_status = False
                return wpt_courant
        elif flight_plan[wpt_courant][TYPE_WPT_FP] == FLYBY:
            if distance_to_go(xy_avion, xy_wpt_dirto) < 2*distance_to_end_leg(xy_avion, xy_wpt_dirto, xy_next_waypoint):
                dirto_status = False
                return wpt_courant
        return wpt_courant
    ####SEQUENCEMENT LEGS
    xy_wpt=[float(flight_plan[wpt_courant+1][X_FP]), float(flight_plan[wpt_courant+1][Y_FP])]
    xy_previous_wpt = [float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP])]
    xy_wpt_suivant = [float(flight_plan[wpt_courant+2][X_FP]), float(flight_plan[wpt_courant+2][Y_FP])]
    distance = distance_to_go(xy_wpt, xy_avion)
    #print("distance entre avion et wpt à séquencer?: ",distance)
    #print("distance dans laquelle il faut séquencer si fly by:",2*distance_to_end_leg(xy_previous_wpt, xy_wpt, xy_wpt_suivant))
    #print("distance overfly:",epsilon_overfly)
    #print("wpt de test : ",flight_plan[wpt_courant+1][nomwpt]," ",flight_plan[wpt_courant+1][type_wpt_fp])
    if flight_plan[wpt_courant+1][TYPE_WPT_FP] == FLYBY:
        if distance < 2*distance_to_end_leg(xy_previous_wpt, xy_wpt, xy_wpt_suivant):
            #print("envoi car flyby\n")
            return wpt_courant+1 #index du waypoint dans le flight plan
    elif flight_plan[wpt_courant+1][TYPE_WPT_FP] == OVERFLY:
        if distance < epsilon_overfly:
            #print("envoi car overfly\n")
            return wpt_courant+1
    #print("pas de séquencement--> on continue sur le même leg\n")
    return wpt_courant ## --> dans le cas ou on continue sur le leg actuel

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
#en sortie : distance à partir de laquelle il faut séquencer le prochain wpt du PDV
def distance_to_end_leg(xy_waypoint1, xy_waypoint2, xy_waypoint3):
    delta_cap_wpt3_wpt1 = axe_cap(xy_waypoint2, xy_waypoint3) - axe_cap(xy_waypoint1, xy_waypoint2)
    vitesse = float(StateVector[SPD_SV]) ##convertir en m/s la string du state vector
    rayon = vitesse**2/(g*math.atan(perf.perfos_avion(volets,landing_gear)['PhiMaxAutomatique']))
    distance_virage = rayon * math.tan(delta_cap_wpt3_wpt1/2)
    distance_virage = math.sqrt(distance_virage**2)
    return distance_virage

#en entrée : deux liste correspondant aux coord x,y waypoint
#en sortie : angle nord GEO entre les deux WPTs 
def axe_cap(xy_waypoint1, xy_waypoint2):
    cap_leg = math.atan2(xy_waypoint2[Y_SV]-xy_waypoint1[Y_SV],xy_waypoint2[X_SV]-xy_waypoint1[X_SV]) #/rapport au Nord GEO
    return cap_leg

#en entrée : x,y de deux waypoints
#en sortie : distance entre les deux waypoints
def distance_to_go(xy_waypoint1, xy_waypoint2):
    distance = math.sqrt((xy_waypoint2[X_SV] - xy_waypoint1[X_SV])**2 + (xy_waypoint2[Y_SV] - xy_waypoint1[Y_SV])**2)
    return distance

#en entrée : x,y du waypoint courant
#en sortie : x,y du waypoint offset
def xy_offset(x_wpt, y_wpt):
    xy_wpt = [float(flight_plan_used[wpt_courant][X_FP]), float(flight_plan_used[wpt_courant][Y_FP])]
    xy_wpt_suivant = [float(flight_plan_used[wpt_courant+1][X_FP]), float(flight_plan_used[wpt_courant+1][Y_FP])]
    cap = axe_cap(xy_wpt, xy_wpt_suivant)
    if offset_side == "L":
        x = x_wpt + offset_dist*math.cos(90-cap)
        y = y_wpt - offset_dist*math.sin(90-cap)
    if offset_side == "R":
        x = x_wpt - offset_dist*math.cos(90-cap)
        y = y_wpt + offset_dist*math.sin(90-cap)
    return [x, y]
#######################################################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_view = MainView()
    main_view.show()

    #Bus IVY
    app_name = "FMGS"
    #bus_Ivy = "127.255.255.255:2010"
    #bus_Ivy = "255.255.248.0.2010"
    #bus_Ivy = "172.20.10.255:2087"
    bus_Ivy = "224.255.255.255:2010"

    def initialisation_FMS (*a):
        IvySendMsg("FGSStatus=Connected")

    def on_die_fms(*a):
        IvySendMsg("FGSStatus=Disconnected")
        IvyStop()

    IvyInit (app_name, "Ready to receive", on_die_fms, initialisation_FMS)
    IvyStart (bus_Ivy)

    IvyBindMsg(on_msg, '^VoletState=(\S+)') #liaison du message Ivy à la fonction on_msg
    IvyBindMsg(sur_msg, '^LandingGearState=(\S+)') #liaison du message Ivy à la fonction sur_msg
    IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')
    IvyBindMsg(on_msg_time, '^Time t=(.*)')
    IvyBindMsg(on_msg_dirto, '^DirTo Wpt=(.*)')
    IvyBindMsg(on_msg_volets, '^VoletState=(.*)')
    IvyBindMsg(on_msg_landing_gear, '^LandingGearState=(.*)')
    IvyBindMsg(on_msg_offset, '^OffSet=(.*) Side=(.*)')
    #IvyMainLoop()
    sys.exit(app.exec_())

    #######################################################################################################################