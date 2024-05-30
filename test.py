import sqlite3
# Création de la base de données et connexion
#nav_db.db : Waypoints (IdWaypoint, waypoint_identifier, x, y)
con = sqlite3.connect('nav_db.db')
cur = con.cursor()
ID_DB, X_DB, Y_DB = 1, 2, 3
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
ALEX = Waypoint(find_waypoint("ALEX")[ID_DB],find_waypoint("ALEX")[X_DB],find_waypoint("ALEX")[Y_DB])
SULLY = Waypoint(find_waypoint("SULLY")[ID_DB],find_waypoint("SULLY")[X_DB],find_waypoint("SULLY")[Y_DB])
MARTIN = Waypoint(find_waypoint("MARTIN")[ID_DB],find_waypoint("MARTIN")[X_DB],find_waypoint("MARTIN")[Y_DB])

import matplotlib.pyplot as plt

# List of waypoints
waypoints = [Seuil1, Seuil2, ESUME, WPT1, WPT2, WPT3, WPTA, WPTB, WPTC, ALEX, SULLY, MARTIN]

# Extract x and y coordinates
x_coords = [waypoint.y for waypoint in waypoints]
y_coords = [waypoint.x for waypoint in waypoints]
names = [waypoint.waypoint_identifier for waypoint in waypoints]

# Plot the waypoints
plt.scatter(x_coords, y_coords)

# Add labels to the waypoints
for i, name in enumerate(names):
    plt.annotate(name, (x_coords[i], y_coords[i]))

# Set labels and title
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Waypoint Locations')

# Show the plot
plt.axis('scaled')
plt.axis([-10000, 10000, -25000, 25000])
plt.show()