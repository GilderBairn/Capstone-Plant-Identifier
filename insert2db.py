import mysql.connector
import json

plantdb = mysql.connector.connect(host='localhost', user='phpmyadmin', passwd='Lizziefarts303!', database='plantid')
curs = plantdb.cursor()

with open('Class_species_mapping.json', 'r') as fp:
    struct = json.load(fp)

for listing in struct.keys():
    sql = 'INSERT INTO species VALUES (%d, "%s", "%s", "%s")'
    values = (int(listing), struct[listing]['Genus'], struct[listing]['Family'], struct[listing]['Species'])
    final = sql % values
    print(final)
    curs.execute(final)

plantdb.commit()
