pymongoSql
===========

Python functions to convert SQL query to mongo query.
At present this is a utility to print how simple SQL select statements will look like as mongo queries.
Best place to see what it can do is the test.py file.

Fix from Parent repo: https://github.com/martinslabber/pysql2mongo

Requirements
============

* python3.9 | python3.10
* pyparsing==3.0.9
* pymongo

Usage Examples
==============

> `python pymongoSql.py`


	The SQL query:  select name, phone_no from users where name = 'bob the builder' and hourly_rate <= 1000

	is this mongo query:  db.users.find({$and:[{name:'bob the builder'}, {hourly_rate:{$lte:1000}}]}, {_id:0, name:1, phone_no:1})

Testing
==============

> `python -m unittest test.py`


	..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.064s
    
    OK


TODO
====
There is so much.

* Skip and Limit
* Orderby

