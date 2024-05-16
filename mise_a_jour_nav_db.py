import sqlite3

con = sqlite3.connect('nav_db.db')    
cur = con.cursor()

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

