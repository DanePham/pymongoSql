pymongoSql
===========

Python functions to convert SQL query to mongo query.
At present this is a utility to print how simple SQL statements will look like as mongo queries.
Best place to see what it can do is the test.py file.

Fix from Parent repo: https://github.com/martinslabber/pysql2mongo

Requirements
============

* python3.9 | python3.10
* pyparsing==3.0.9
* pymongo==4.3.2

Usage Examples
==============

> Edit file `sqlExample.py` with this guide below


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
> After edit file sqlExample.py, we run this file by command `python sqlExample.py`

TODO
====
There is so much.

* Skip and Limit
* Orderby

