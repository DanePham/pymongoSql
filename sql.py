from src import sqlMongo

sql = "SELECT * FROM order" # pass your sql statement here

cursor = sqlMongo(
    dbname="restaurant", # pass your database name here
    user=None, # pass your username here
    password=None, # pass your password of username here
    host="localhost", # pass your HOSTNAME name here
    port=27017 # pass your port of mongodb here
).execute(sql)

data = list(cursor)

print(data)