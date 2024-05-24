import sqlite3

# Création de la base de données et connexion
con = sqlite3.connect('nav_db.db')
cur = con.cursor()

cur.execute('''CREATE TABLE Waypoints (
                IdWaypoint INTEGER PRIMARY KEY AUTOINCREMENT,
                waypoint_identifier TEXT,
                x TEXT,
                y TEXT
            )''')

waypoints = open("csv/waypoints.csv", "r") #waypoints.csv : IdWaypoints (autoincrement),waypoints_identifier x, y (all text)

dbwaypoints = []

for ligne in waypoints :   #pour chaque ligne du fichier csv
    dbwaypoints.append(ligne.split(sep=';'))   #rajoute à une liste une liste contenant chaque élement de la ligne
for item in dbwaypoints :
    cur.execute("""
    INSERT INTO Waypoints (waypoint_identifier, x, y) VALUES (?,?,?)""",(item[0],item[1],item[2]))
    con.commit()
    print("les éléments suivants ont été ajoutés à la database waypoints",item[0],item[1],item[2],"\n")

waypoints.close

# Fermeture de la connexion à la base de données
con.close()