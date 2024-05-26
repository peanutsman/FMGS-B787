import sqlite3
import performances as perf
import math
import conversion as c

# Création de la base de données et connexion
#nav_db.db : Waypoints (IdWaypoint, waypoint_identifier, x, y)
con = sqlite3.connect('nav_db.db')
cur = con.cursor()

###Index de liste
dbid = 1
dbx = 2
dby = 3
###Constantes
overfly = 0
flyby = 1
undefined_z = -1
#Initialisation des variables
V2 = perf.perfos_avion('0',0)["V2"]
MinMach = perf.perfos_avion('0',0)["MinMach"]
VMO = perf.perfos_avion('0',0)["VMO"]
MMO = perf.perfos_avion('0',0)["MMO"]


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
        return ((VMO-V2)/100)*CI + V2
    if CI > 100:
        return VMO

#en entrée : N/A
#en sortie : vitesse managée en fonction du cost index    
def cost_index_mach():
    if CI in range(0, 100):
        return ((MMO-MinMach)/100)*CI + MinMach
    if CI > 100:
        return MMO

## Sinon on oublie la DB et on met diretement les coordonnées ici, dans tous les cas on peut garder les deux, la DB pour des points permanenents
#et la création d'autres waypoints ici pour des points temporaires/pour les tests

####AJOUT DES WAYPOINTS
####Class waypoint : waypoint_identifier, x, y
Seuil1 = Waypoint(find_waypoint("01L")[dbid],find_waypoint("01L")[dbx],find_waypoint("01L")[dby])
Seuil2 = Waypoint(find_waypoint("19R")[dbid],find_waypoint("19R")[dbx],find_waypoint("19R")[dby])
ESUME = Waypoint(find_waypoint("ESUME")[dbid],find_waypoint("ESUME")[dbx],find_waypoint("ESUME")[dby])
WPT1 = Waypoint(find_waypoint("WPT1")[dbid],find_waypoint("WPT1")[dbx],find_waypoint("WPT1")[dby])
WPT2 = Waypoint(find_waypoint("WPT2")[dbid],find_waypoint("WPT2")[dbx],find_waypoint("WPT2")[dby])
WPT3 = Waypoint(find_waypoint("WPT3")[dbid],find_waypoint("WPT3")[dbx],find_waypoint("WPT3")[dby])
WPTA = Waypoint(find_waypoint("WPTA")[dbid],find_waypoint("WPTA")[dbx],find_waypoint("WPTA")[dby])
WPTB = Waypoint(find_waypoint("WPTB")[dbid],find_waypoint("WPTB")[dbx],find_waypoint("WPTB")[dby])
WPTC = Waypoint(find_waypoint("WPTC")[dbid],find_waypoint("WPTC")[dbx],find_waypoint("WPTC")[dby])


###DIFFERENTS FLIGHT PLANS
#Flight plan : [waypoint_identifier, x, y, flyby/overfly, z]
#indice :      [0,                    1, 2, 3,            4]
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

fp_test1 = []
fp_test1.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,overfly,0])
fp_test1.append([Seuil2.waypoint_identifier,Seuil2.x,Seuil2.y,overfly,0])
fp_test1.append([ESUME.waypoint_identifier,ESUME.x,ESUME.y,overfly,undefined_z])
fp_test1.append([WPT1.waypoint_identifier,WPT1.x,WPT1.y,overfly,undefined_z])
fp_test1.append([WPT2.waypoint_identifier,WPT2.x,WPT2.y,overfly,undefined_z])
fp_test1.append([WPT3.waypoint_identifier,WPT3.x,WPT3.y,overfly,undefined_z])
fp_test1.append([Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,overfly,0])


#### DEFINITION DES PARAMETRES COST INDEX ET VEND
CI = 0
V_vent = 0 # en knots
Dir_Vent = 94 #degrés d'ou il vient
V_Init = 400 ## en knots
Gamma_Init = 0 ## en degrés
trans_alt = 5000 ## en ft
VMAXFL100 = 250 ## en knots
wind = [c.knots_to_ms(V_vent), c.deg_to_rad(Dir_Vent)+math.pi]
flight_plan = fp_test1