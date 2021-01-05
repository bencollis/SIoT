import sqlite3

conn=sqlite3.connect('../sensorsData.db')
curs=conn.cursor()
for row in curs.execute("SELECT * FROM trash_data ORDER BY timestamp DESC LIMIT 1"):
    time = str(row[0])
conn.close()
print(time)