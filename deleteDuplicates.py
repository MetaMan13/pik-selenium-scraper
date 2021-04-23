import os, codecs, requests, mysql.connector, pathlib, shutil, stat

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password = "",
    database="net_doo"
)

mycursor = mydb.cursor(buffered=True)
# sql = "SELECT name, COUNT(name) FROM products GROUP BY name HAVING COUNT(name) > 1"
sql = "SELECT MAX(id) FROM products"
mycursor.execute(sql)
mydb.commit()
print(mycursor.fetchone()[0])