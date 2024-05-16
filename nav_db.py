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



# Fermeture de la connexion à la base de données
con.close()