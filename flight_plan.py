import sqlite3

# Création de la base de données et connexion
con = sqlite3.connect('nav_db.db')
cur = con.cursor()

class Waypoint:
    def __init__(self, waypoint_identifier, x, y):
        self.waypoint_identifier = waypoint_identifier
        self.x = x
        self.y = y

#nav_db.db : Waypoints (IdWaypoint, waypoint_identifier, x, y)
def find_waypoint(waypoint_identifier):
    waypoint = cur.execute("SELECT * FROM Waypoints WHERE waypoint_identifier = ?",([waypoint_identifier])).fetchone()
    return waypoint

def cost_index_speed():
    global CI
    if CI == 0:
        return 200
    if CI > 100:
        return 300
    else :
        return 275

## Sinon on oublie la DB et on met diretement les coordonnées ici, dans tous les cas on peut garder les deux, la DB pour des points permanenents
#et la création d'autres waypoints ici pour des points temporaires/pour les tests

Seuil1 = Waypoint(find_waypoint("01L")[1],find_waypoint("01L")[2],find_waypoint("01L")[3])
Seuil2 = Waypoint(find_waypoint("19R")[1],find_waypoint("19R")[2],find_waypoint("19R")[3])
ESUME = Waypoint(find_waypoint("ESUME")[1],find_waypoint("ESUME")[2],find_waypoint("ESUME")[3])
WPT1 = Waypoint(find_waypoint("WPT1")[1],find_waypoint("WPT1")[2],find_waypoint("WPT1")[3])

overfly = 0
flyby = 1
undefined_z = -1

flight_plan_tour_de_piste_GAUCHE = []
fptdpG =[] ##Flight Plan Tour De Piste Gauche
CI = 0
fptdpG.append(Seuil1.waypoint_identifier,Seuil1.x,Seuil1.y,overfly,0)
fptdpG.append(ESUME.waypoint_identifier,ESUME.x,ESUME.y,flyby,undefined_z)
fptdpG.append(WPT1.waypoint_identifier,WPT1.x,WPT1.y,flyby,undefined_z)
fptdpG.append(Seuil2.waypoint_identifier,Seuil2.x,Seuil2.y,overfly,0)



