import sqlite3
import performances as perf
import math

# Création de la base de données et connexion
con = sqlite3.connect('nav_db.db')
cur = con.cursor()

###CONSTANTS
overfly = 0
flyby = 1
undefined_z = -1
####

V2 = perf.perfos_avion('0',0)["V2"]
MinMach = perf.perfos_avion('0',0)["MinMach"]

def VMO():
    return perf.perfos_avion('0',0)["VMO"]
def MMO():
    return perf.perfos_avion('0',0)["MMO"]

class Waypoint:
    def __init__(self, waypoint_identifier, x, y):
        self.waypoint_identifier = waypoint_identifier
        self.x = x
        self.y = y

#nav_db.db : Waypoints (IdWaypoint, waypoint_identifier, x, y)
def find_waypoint(waypoint_identifier: str):
    waypoint = cur.execute("SELECT * FROM Waypoints WHERE waypoint_identifier = ?",([waypoint_identifier])).fetchone()
    return waypoint

def find_waypoint_index_in_fp(waypoint_identifier: str, flight_plan: list):
    for i in range(len(flight_plan)):
        if flight_plan[i][0] == waypoint_identifier:
            return i
    return -1

def knots_to_ms(knots):
    return knots*0.514444

def deg_to_rad(deg):
    return deg * math.pi / 180

def cost_index_ias():
    if CI in range(0, 100):
        return ((VMO()-V2)/100)*CI + V2
    if CI > 100:
        return VMO()
    
def cost_index_mach():
    if CI in range(0, 100):
        return ((MMO()-MinMach)/100)*CI + MinMach
    if CI > 100:
        return MMO()

def speed_to_mach(speed):
    return speed/600

def mach_to_speed(mach):
    return mach*600
## Sinon on oublie la DB et on met diretement les coordonnées ici, dans tous les cas on peut garder les deux, la DB pour des points permanenents
#et la création d'autres waypoints ici pour des points temporaires/pour les tests

####AJOUT DES WAYPOINTS
####Class waypoint : waypoint_identifier, x, y, z
Seuil1 = Waypoint(find_waypoint("01L")[1],find_waypoint("01L")[2],find_waypoint("01L")[3])
Seuil2 = Waypoint(find_waypoint("19R")[1],find_waypoint("19R")[2],find_waypoint("19R")[3])
ESUME = Waypoint(find_waypoint("ESUME")[1],find_waypoint("ESUME")[2],find_waypoint("ESUME")[3])
WPT1 = Waypoint(find_waypoint("WPT1")[1],find_waypoint("WPT1")[2],find_waypoint("WPT1")[3])
WPTA = Waypoint(find_waypoint("WPTA")[1],find_waypoint("WPTA")[2],find_waypoint("WPTA")[3])
WPTB = Waypoint(find_waypoint("WPTB")[1],find_waypoint("WPTB")[2],find_waypoint("WPTB")[3])
WPTC = Waypoint(find_waypoint("WPTC")[1],find_waypoint("WPTC")[2],find_waypoint("WPTC")[3])

#### DEFINITION DES PARAMETRES COST INDEX ET VEND
CI = 0
V_vent = 20 #knots
Dir_Vent = 94
V_Init = 150 ## en knots
Gamma_Init = 0

wind = [knots_to_ms(V_vent), deg_to_rad(Dir_Vent)+math.pi]

###DIFFERENTS FLIGHT PLANS
fptdpG =[] ##Flight Plan Tour De Piste Gauche
fptdpG.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,overfly,0])
fptdpG.append([ESUME.waypoint_identifier,ESUME.x,ESUME.y,flyby,undefined_z])
fptdpG.append([WPT1.waypoint_identifier,WPT1.x,WPT1.y,flyby,undefined_z])
fptdpG.append([Seuil2.waypoint_identifier,Seuil2.x,Seuil2.y,overfly,0])

fp_test = []
fp_test.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,overfly,0])
fp_test.append([WPTA.waypoint_identifier,WPTA.x,WPTA.y,flyby,undefined_z])
fp_test.append([WPTB.waypoint_identifier,WPTB.x,WPTB.y,flyby,undefined_z])
fp_test.append([WPTC.waypoint_identifier,WPTC.x,WPTC.y,flyby,undefined_z])



