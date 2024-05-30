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
NOMWPT_FP, X_FP, Y_FP, TYPE_WPT_FP,ALT_FP = 0, 1, 2, 3, 4
#Index des éléments du state vector
X_SV, Y_SV, ALT_SV, SPD_SV = 0, 1, 2, 3
#Index des éléments dans les listes x,y
X, Y = 0, 1
#Index du waypoint dans le flight plan
FIRST_WPT = 0
#Index des données de vent
V_VENT, DIR_VENT = 0, 1
#Constantes
FACTEUR = 2 #facteur de sécurité pour le epsilon_overfly 
OVERFLY, FLYBY = 0, 1
TRANS_ALT_FT = int(fp.trans_alt)
IASMAXFL100, FL100_FT = fp.VMAXFL100, 10000
LGDOWN, LGUP = 0, 1
#Initialisation des variables globales
t_minus_1 = 0
StateVector, volets, landing_gear = [0, 0, 0, 0, 0, 0, 0], '0', LGDOWN
dirto_status = False
offset_status, offset_dist, offset_side = None, None, None
epsilon_overfly = 200.0
declinaison = perf.perfos_avion(volets,landing_gear,0)['MagneticDeclination']
flight_plan_used, wpt_courant = fp.flight_plan, 0


#en entrée : state vector sur le bus IVY
#en sortie : acquisition du statevector en variable globale, envoi de la vitesse managée, envoi des legs, envoi de l'altitude managée, des perfos
def on_msg_StateVector(agent, *data :tuple):
    global StateVector
    StateVector = data 
    ###ENVOI DE LA VITESSE MANAGEE
    envoi_vitesse()
    ###ENVOIE DES LEGS
    envoi_leg(flight_plan_used)
    ####ENVOI DE L'ALTITUDE MANAGEE
    envoi_altitude(flight_plan_used)
    ###ENVOI DES PERFOS
    envoi_perfo()

#en entrée : temps sur le bus IVY
#en sortie : initialisation du state vector et envoi des perfos, du vent
def on_msg_time(agent, *data):
    ###INITIALISATION DE LA SIMULATION
    if data[0] == "1.00":
        init_simulation()
    ####MAJ DE L'EPSILON OVERFLY
    maj_epsilon_overfly(float(data[0]))

#en entrée : statut des volets sur le bus IVY
#en sortie : changement du statut des volets (variable globale)
def on_msg_volets(agent, *statut_volet):
    global volets
    volets = statut_volet[0]
    try:
        pos = int(volets) #conversion de la position en entier
        main_view.signal_update_posi.emit(pos) #emit signal
    except ValueError:
        print(f"Invalid position received: {volets}")

#en entrée : statut du train d'atterrissage sur le bus IVY
#en sortie : changement du statut du train d'atterrissage (variable globale)
def on_msg_landing_gear(agent, *statut_landing_gear):
    global landing_gear
    if statut_landing_gear[0]=="False":
        landing_gear = LGDOWN
        print("L/G GEAR DOWN")
    else:
        landing_gear = LGUP
        print("L/G GEAR UP")
    try:
        pos = landing_gear
        main_view.signal_update_train.emit(pos)
    except ValueError:
        print(f"Invalid position received: {landing_gear}")

#en entrée : wpt = [nom_waypoint]
#en sortie : changement du WPT séquencé (variable globale)
def on_msg_dirto(agent, *wpt: tuple):
    global dirto_status, wpt_courant
    dirto = fp.find_waypoint_index_in_fp(wpt[0], flight_plan_used)
    if dirto == -1:
        print("Waypoint non trouvé dans le flight plan")
    else:
        wpt_courant = dirto
        dirto_status = True
        print("DIRTO to %s WPT\n" %(flight_plan_used[wpt_courant][NOMWPT_FP]))

#en entrée : offset = [distance, side]
#en sortie : changement du statut de l'offset (variable globale)
def on_msg_offset(agent, *offset: tuple):
    global offset_status, offset_dist, offset_side
    if float(offset[0]) > 0 and offset[1] in ["L", "R"]:
        offset_status = True
        offset_dist = c.nm_to_m(float(offset[0]))
        offset_side = offset[1]
        if dirto_status == False:
            print("\n%s%s OFFSET ACTIVATED" %(offset[0], offset_side))
        else:
            print("\n%s%s OFFSET WHEN DIRTO FINISHED" %(offset[0],offset_side))
    else:
        print("Format de l'OFFSET incorrect")
        offset_status = False

#en entrée : N/A
#en sortie : envoi state vector, envoi vent, envoit déclinaison magnétique
def init_simulation():
    global wpt_courant, t_minus_1, epsilon_overfly, landing_gear, dirto_status, offset_status, volets, StateVector
    wpt_courant = 0
    t_minus_1 = 0
    StateVector, volets, landing_gear = [0, 0, 0, 0, 0, 0, 0], '0', LGDOWN
    dirto_status = False
    offset_status = None
    epsilon_overfly = 200.0
    ###ENVOI DU STATE VECTOR
    envoi_init_state_vector()
    ###ENVOI DU VENT
    envoi_vent()
    ###ENVOIE DE LA DECLINAISON MAGNETIQUE
    envoi_declinaison()

#en entrée : N/A
#en sortie : envoi du state vector initial sur le bus IVY
def envoi_init_state_vector():
    x_premier_wpt = float(flight_plan_used[FIRST_WPT][X_FP])
    y_premier_wpt = float(flight_plan_used[FIRST_WPT][Y_FP])
    xy_premier_wpt = [x_premier_wpt, y_premier_wpt]
    xy_deuxieme_wpt = [float(flight_plan_used[FIRST_WPT+1][X_FP]), float(flight_plan_used[FIRST_WPT+1][Y_FP])]
    windspeed = fp.wind[V_VENT]
    QFU = axe_cap(xy_premier_wpt, xy_deuxieme_wpt)
    derive =math.asin(windspeed*math.sin(QFU-c.deg_to_rad(fp.Dir_Vent))/(c.knots_to_ms(fp.V_Init)*math.cos(c.deg_to_rad(fp.Gamma_Init))))
    cap_vent_piste = QFU -  derive 
    Z0 = c.feet_to_meters(fp.Z_Init)
    V0 = c.knots_to_ms(c.ias_to_tas(fp.V_Init, fp.Z_Init))
    print("V0",V0)
    IvySendMsg("InitStateVector x=%s y=%s z=%s Vp=%s fpa=0.0000 psi=%s phi=0.0000" %(str(x_premier_wpt), str(y_premier_wpt),Z0, V0, str(cap_vent_piste)))

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
    perfos = perf.perfos_avion(volets, landing_gear, float(StateVector[ALT_SV]))
    IvySendMsg("Performances NxMax=%s NxMin=%s NzMax=%s NzMin=%s PMax=%s PMin=%s AlphaMax=%s AlphaMin=%s PhiMaxManuel=%s PhiMaxAutomatique=%s GammaMax=%s GammaMin=%s Vmo=%s Vmin=%s Mmo=%s Mmin=%s" %(perfos["NxMax"], perfos["NxMin"], perfos["NzMax"], perfos["NzMin"], perfos["PMax"], perfos["PMin"], perfos["AlphaMax"], perfos["AlphaMin"], perfos["PhiMaxManuel"], perfos["PhiMaxAutomatique"], perfos["GammaMax"], perfos["GammaMin"], perfos["VMO"], perfos["V2"], perfos["MMO"], perfos["MinMach"]))

#en entrée : N/A
#en sortie : envoi de la vitesse/mach managée sur le bus IVY
def envoi_vitesse():
    alt = c.meters_to_feet(float(StateVector[ALT_SV]))
    print("Altitude en ft",alt)
    ###IAS ou altitude sous la trans alt
    if int(alt) in range(0,TRANS_ALT_FT):
        ias = fp.cost_index_ias()
        print("ias en knots",ias)
        if ias > IASMAXFL100 and alt < FL100_FT:
            ias = c.knots_to_ms(IASMAXFL100)
        else:
            ias = c.knots_to_ms(ias)
        IvySendMsg("Statut=Vc MachManaged=0 VcManaged=%s" %ias)
        return
    ###CAS ou altitude au dessus de la trans alt
    if alt > TRANS_ALT_FT:
        mach = fp.cost_index_mach()
        if alt < FL100_FT and c.mach_to_tas(mach) > c.ias_to_tas(IASMAXFL100,alt):
            mach = c.tas_to_mach(c.ias_to_tas(IASMAXFL100, alt))
        IvySendMsg("Statut=Mach MachManaged=%s VcManaged=0" %mach)
        return
    IvySendMsg("Statut=Vc MachManaged=0 VcManaged=%s" %(c.knots_to_ms(fp.cost_index_ias())))
    

#en entrée : flight plan (liste de waypoints, type,altitude)
#en sortie : envoi de l'altitude managée du wpt du début de leg sur le bus IVY
def envoi_altitude(flight_plan :list):
    if wpt_courant == len(flight_plan)-1:
        altitude = flight_plan[wpt_courant][ALT_FP]
    else:
        altitude = flight_plan[wpt_courant+1][ALT_FP]
    if altitude == fp.UNDEFINED_Z and float(StateVector[ALT_SV]) >= 0:
        altitude = StateVector[ALT_SV]
    else:
        altitude = 1
    IvySendMsg("ZcManaged=%s" %altitude)

#en entrée : x,y de deux waypoints
#en sortie : envoi des coordonnées du waypoint de départ et du cap du leg sur le bus IVY
def envoi_axe(xy_waypoint1: list, xy_waypoint2 : list):
    cap_axe = axe_cap(xy_waypoint1, xy_waypoint2)
    IvySendMsg("AxeFlightPlan LegX=%s LegY=%s LegCap=%s" %(xy_waypoint1[X_SV],  xy_waypoint1[Y_SV], cap_axe))
    #IvySendMsg("InitStateVector x=%s y=%s z=%s Vp=%s fpa=0.0000 psi=%s phi=0.0000" %(StateVector[X_SV], StateVector[Y_SV], StateVector[ALT_SV], c.knots_to_ms(c.ias_to_tas(fp.V_Init,0)),cap_axe))

#en entrée : flight plan (liste de waypoints, type,altitude)
#en sortie : changement du WPT séquencé (variable globale)
def envoi_leg(flight_plan :list):
    global wpt_courant
    wpt_courant = sequencement_leg(flight_plan)
    xy_avion = [float(StateVector[X_SV]), float(StateVector[Y_SV])]
    if offset_status == True and dirto_status == False:
        xy_wpt_courant = xy_offset(float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP]))
    else:
        xy_wpt_courant = [float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP])]
        print("Waypoint courant ",flight_plan[wpt_courant][NOMWPT_FP],xy_wpt_courant)
    if dirto_status == True or wpt_courant == len(flight_plan)-1:
        print("envoie axe car dirto")
        envoi_axe(xy_avion, xy_wpt_courant)
        return
    elif offset_status == True and dirto_status == False:
        xy_wpt_suivant = xy_offset(float(flight_plan[wpt_courant+1][X_FP]), float(flight_plan[wpt_courant+1][Y_FP]))
    else:
        xy_wpt_suivant = [float(flight_plan[wpt_courant+1][X_FP]), float(flight_plan[wpt_courant+1][Y_FP])]
    print("envoi axe normal entre ",xy_wpt_courant, xy_wpt_suivant)
    envoi_axe(xy_wpt_courant, xy_wpt_suivant)

#en entrée : flight plan (liste de waypoints, type,altitude)
#en sortie : index du waypoint à séquencer en fonction des angles de virage et de la position avion
def sequencement_leg(flight_plan :list[list]):
    global dirto_status, wpt_courant
    xy_avion = [float(StateVector[X_SV]), float(StateVector[Y_SV])]
    ###SI dernier leg OU si Wpt_courant = le dernier WPT du PDV --> envoi du dernier leg
    if wpt_courant == len(flight_plan)-1:
        return wpt_courant
    if dirto_status == False and wpt_courant == len(flight_plan)-2:
        return wpt_courant
    ####DIR TO
    if dirto_status == True:
        wpt_index_after_dirto = wpt_courant+1
        xy_wpt_dirto = [float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP])]
        xy_next_waypoint = [float(flight_plan[wpt_index_after_dirto][X_FP]), float(flight_plan[wpt_index_after_dirto][Y_FP])]
        if flight_plan[wpt_courant][TYPE_WPT_FP] == OVERFLY:
            if distance_to_go(xy_avion, xy_wpt_dirto) < epsilon_overfly:
                dirto_status = False
                print("DIRTO FINISHED within distance epsilon", epsilon_overfly)
                return wpt_courant
        elif flight_plan[wpt_courant][TYPE_WPT_FP] == FLYBY:
            if distance_to_go(xy_avion, xy_wpt_dirto) < distance_to_end_leg(xy_avion, xy_wpt_dirto, xy_next_waypoint):
                dirto_status = False
                print("DIRTO FINISHED within distance", distance_to_end_leg(xy_avion, xy_wpt_dirto, xy_next_waypoint))
                return wpt_courant
        return wpt_courant
    ####SEQUENCEMENT LEGS
    xy_wpt=[float(flight_plan[wpt_courant+1][X_FP]), float(flight_plan[wpt_courant+1][Y_FP])]
    xy_previous_wpt = [float(flight_plan[wpt_courant][X_FP]), float(flight_plan[wpt_courant][Y_FP])]
    xy_wpt_suivant = [float(flight_plan[wpt_courant+2][X_FP]), float(flight_plan[wpt_courant+2][Y_FP])]
    distance = distance_to_go(xy_wpt, xy_avion)
    if flight_plan[wpt_courant+1][TYPE_WPT_FP] == FLYBY:
        print("\nFLYBY vers le waypoint %s distance avion et wpt" %(flight_plan[wpt_courant+1][NOMWPT_FP]), distance," distance dans laquelle séquencer", distance_to_end_leg(xy_previous_wpt, xy_wpt, xy_wpt_suivant))
        if distance < distance_to_end_leg(xy_previous_wpt, xy_wpt, xy_wpt_suivant):
            print("\n\n\nSequencement prochaine WAYPOINT\n\n")
            return wpt_courant+1 #on change de leg car on arrive dans la condition flyby
    elif flight_plan[wpt_courant+1][TYPE_WPT_FP] == OVERFLY:
        print("\nOVERFLY vers le waypoint %s distance avion et wpt" %(flight_plan[wpt_courant+1][NOMWPT_FP]), distance," distance dans laquelle séquencer", epsilon_overfly)
        if distance < epsilon_overfly:
            print("\n\n\nSequencement prochaine WAYPOINT\n\n")
            return wpt_courant+1 #on change de leg car on arrive dans la condition flyover
    return wpt_courant ## --> dans le cas ou on continue sur le leg actuel

#en entrée : liste correspondant au waypoint dans le flight plan ([waypoint_identifier, x, y, z,overfly/flyby]) 
#en sortie : distance à partir de laquelle il faut séquencer le prochain wpt du PDV
def distance_to_end_leg(xy_waypoint1, xy_waypoint2, xy_waypoint3):
    delta_cap_wpt3_wpt1 = axe_cap(xy_waypoint2, xy_waypoint3) - axe_cap(xy_waypoint1, xy_waypoint2)
    print("delta cap ",c.rad_to_deg(delta_cap_wpt3_wpt1))
    vitesse = float(StateVector[SPD_SV]) ##convertir en m/s la string du state vector
    print("vitesse en m/s",vitesse)
    print("tan de phi",math.tan(perf.perfos_avion(volets,landing_gear,float(StateVector[ALT_SV]))['PhiMaxAutomatique'])) #vérifier que la valeur est correcte
    rayon = vitesse**2/(g*math.tan(perf.perfos_avion(volets,landing_gear,float(StateVector[ALT_SV]))['PhiMaxAutomatique']))
    print("rayon",rayon)
    print("tan de delta cap",math.tan(delta_cap_wpt3_wpt1/2))
    distance_virage = rayon * math.tan(delta_cap_wpt3_wpt1/2)
    print("distance virage",distance_virage)
    distance_virage = math.sqrt(distance_virage**2)

    return distance_virage

#en entrée : deux liste correspondant aux coord x,y waypoint
#en sortie : angle nord GEO entre les deux WPTs 
def axe_cap(xy_waypoint1, xy_waypoint2):
    cap_leg = math.atan2(xy_waypoint2[Y]-xy_waypoint1[Y],xy_waypoint2[X]-xy_waypoint1[X]) #/rapport au Nord GEO
    return cap_leg

#en entrée : x,y de deux waypoints
#en sortie : distance entre les deux waypoints
def distance_to_go(xy_waypoint1, xy_waypoint2):
    distance = math.sqrt((xy_waypoint2[X] - xy_waypoint1[X])**2 + (xy_waypoint2[Y] - xy_waypoint1[Y])**2)
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
    bus_Ivy = "127.255.255.255:2010"
    #bus_Ivy = "254.255.255.255:2010"
    #bus_Ivy = "192.168.131.255:2087"
    #bus_Ivy = "192.168.161.255:2087"
    #bus_Ivy = "127.255.255.255:2010"
    #bus_Ivy = "224.255.255.255:2010"
    #bus_Ivy = "192.168.141.255:2087"
    def initialisation_FMS (*a):
        IvySendMsg("FGSStatus=Connected")

    def on_die_fms(*a):
        IvySendMsg("FGSStatus=Disconnected")
        IvyStop()

    IvyInit (app_name, "Ready to receive", on_die_fms, initialisation_FMS)
    IvyStart (bus_Ivy)

    IvyBindMsg(on_msg_StateVector, '^StateVector x=(.*) y=(.*) z=(.*) Vp=(.*) fpa=(.*) psi=(.*) phi=(.*)')
    IvyBindMsg(on_msg_time, '^Time t=(.*)')
    IvyBindMsg(on_msg_dirto, '^DirTo Wpt=(.*)')
    IvyBindMsg(on_msg_volets, '^VoletState=(.*)')
    IvyBindMsg(on_msg_landing_gear, '^LandingGearState=(.*)')
    IvyBindMsg(on_msg_offset, '^OffSet=(.*) Side=(.*)')
    sys.exit(app.exec_())


#######################################################################################################################