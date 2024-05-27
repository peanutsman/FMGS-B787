import sqlite3
import performances as perf
import math
import conversion as c

# Création de la base de données et connexion
#nav_db.db : Waypoints (IdWaypoint, waypoint_identifier, x, y)
con = sqlite3.connect('nav_db.db')
cur = con.cursor()

###Index de liste
ID_DB, X_DB, Y_DB = 1, 2, 3
###Constantes
OVERFLY, FLYBY, UNDEFINED_Z = 0, 1, -1
#Initialisation des variables
V2_IAS, VMO_IAS = c.ms_to_knots(perf.perfos_avion('0',0)["V2"]), c.ms_to_knots(perf.perfos_avion('0',0)["VMO"])
MIN_MACH, MMO = perf.perfos_avion('0',0)["MinMach"], perf.perfos_avion('0',0)["MMO"]


class Waypoint:
    def __init__(self, waypoint_identifier, x, y):
        self.waypoint_identifier = waypoint_identifier
        self.x = x
        self.y = y

#en entrée : nom du WPT
#en sortie : waypoint : tuple
def find_waypoint(waypoint_identifier: str):
    waypoint = cur.execute("SELECT * FROM Waypoints WHERE waypoint_identifier = ?",([waypoint_identifier])).fetchone()
    return waypoint

#en entrée : nom du WPT et plan de vol
#en sortie : index du WPT dans le plan de vol
def find_waypoint_index_in_fp(waypoint_identifier: str, flight_plan: list):
    for i in range(len(flight_plan)):
        if flight_plan[i][0] == waypoint_identifier:
            return i
    return -1

#en entrée : N/A
#en sortie : vitesse managée en fonction du cost index
def cost_index_ias():
    if CI in range(0, 100):
        return ((VMO_IAS-V2_IAS)/100)*CI + V2_IAS
    if CI > 100:
        return VMO_IAS

#en entrée : N/A
#en sortie : vitesse managée en fonction du cost index    
def cost_index_mach():
    if CI in range(0, 100):
        return ((MMO-MIN_MACH)/100)*CI + MIN_MACH
    if CI > 100:
        return MMO

## Sinon on oublie la DB et on met diretement les coordonnées ici, dans tous les cas on peut garder les deux, la DB pour des points permanenents
#et la création d'autres waypoints ici pour des points temporaires/pour les tests

####AJOUT DES WAYPOINTS
####Class waypoint : waypoint_identifier, x, y
Seuil1 = Waypoint(find_waypoint("01L")[ID_DB],find_waypoint("01L")[X_DB],find_waypoint("01L")[Y_DB])
Seuil2 = Waypoint(find_waypoint("19R")[ID_DB],find_waypoint("19R")[X_DB],find_waypoint("19R")[Y_DB])
ESUME = Waypoint(find_waypoint("ESUME")[ID_DB],find_waypoint("ESUME")[X_DB],find_waypoint("ESUME")[Y_DB])
WPT1 = Waypoint(find_waypoint("WPT1")[ID_DB],find_waypoint("WPT1")[X_DB],find_waypoint("WPT1")[Y_DB])
WPT2 = Waypoint(find_waypoint("WPT2")[ID_DB],find_waypoint("WPT2")[X_DB],find_waypoint("WPT2")[Y_DB])
WPT3 = Waypoint(find_waypoint("WPT3")[ID_DB],find_waypoint("WPT3")[X_DB],find_waypoint("WPT3")[Y_DB])
WPTA = Waypoint(find_waypoint("WPTA")[ID_DB],find_waypoint("WPTA")[X_DB],find_waypoint("WPTA")[Y_DB])
WPTB = Waypoint(find_waypoint("WPTB")[ID_DB],find_waypoint("WPTB")[X_DB],find_waypoint("WPTB")[Y_DB])
WPTC = Waypoint(find_waypoint("WPTC")[ID_DB],find_waypoint("WPTC")[X_DB],find_waypoint("WPTC")[Y_DB])


###DIFFERENTS FLIGHT PLANS
#Flight plan : [waypoint_identifier, x, y, flyby/overfly, z]
#indice :      [0,                    1, 2, 3,            4]
fptdpG =[] ##Flight Plan Tour De Piste Gauche
fptdpG.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,OVERFLY,0])
fptdpG.append([ESUME.waypoint_identifier,ESUME.x,ESUME.y,FLYBY,UNDEFINED_Z])
fptdpG.append([WPT1.waypoint_identifier,WPT1.x,WPT1.y,FLYBY,UNDEFINED_Z])
fptdpG.append([Seuil2.waypoint_identifier,Seuil2.x,Seuil2.y,OVERFLY,0])

fp_test = []
fp_test.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,OVERFLY,0])
fp_test.append([WPTA.waypoint_identifier,WPTA.x,WPTA.y,FLYBY,UNDEFINED_Z])
fp_test.append([WPTB.waypoint_identifier,WPTB.x,WPTB.y,FLYBY,UNDEFINED_Z])
fp_test.append([WPTC.waypoint_identifier,WPTC.x,WPTC.y,FLYBY,UNDEFINED_Z])

fp_test1 = []
fp_test1.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,OVERFLY,0])
fp_test1.append([Seuil2.waypoint_identifier,Seuil2.x,Seuil2.y,OVERFLY,0])
fp_test1.append([ESUME.waypoint_identifier,ESUME.x,ESUME.y,OVERFLY,UNDEFINED_Z])
fp_test1.append([WPT1.waypoint_identifier,WPT1.x,WPT1.y,OVERFLY,UNDEFINED_Z])
fp_test1.append([WPT2.waypoint_identifier,WPT2.x,WPT2.y,OVERFLY,UNDEFINED_Z])
fp_test1.append([WPT3.waypoint_identifier,WPT3.x,WPT3.y,OVERFLY,UNDEFINED_Z])
fp_test1.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,OVERFLY,0])


#### DEFINITION DES PARAMETRES COST INDEX ET VEND
CI = 0
V_vent = 30 # en knots
Dir_Vent = 120 #degrés d'ou il vient
V_Init = 100 ## en knots IAS
Z_Init = 0 ## en ft
Gamma_Init = 0 ## en degrés
trans_alt = 5000 ## en ft
VMAXFL100 = 250 ## en knots
wind = [c.knots_to_ms(V_vent), c.deg_to_rad(Dir_Vent)+math.pi]
flight_plan = fp_test1
#flight_plan = f.points