from src import sqlMongo

sql = "" # pass your sql - Ex: SELECT * FROM users

cursor = sqlMongo(
    dbname="dbname", # pass your database name here
    user=None, # pass your username here
    password=None, # pass your password of username here
    host="localhost", # pass your HOSTNAME name here
    port=27017 # pass your port of mongodb here
).execute(sql)

data = list(cursor) # convert cursor to any data type u want - Ex: dict, tuple. Here we use list

print(data)