from pymongo import MongoClient
from src.sqlCompiler import create_mongo_shell_query, sql_to_spec


class sqlMongo:
    
    def __init__(
        self,
        dbname: str,
        user: str or None,
        password: str or None,
        host: str,
        port: str = None,
        verbose=True,
        **kwargs,
    ) -> None:
        """
        Initializes sqlMongo.

        Args:
            dbname (str): The name of the database to connect to.
            user (str): The user with which to connect to the database with.
            password (str): The login password for the user.
            host (str): Path to host address for database.
            port (str): Port on which the database is running.
            **kwargs: Additional settings for creating SQLAlchemy engine and connection
        """
        self.dbname = dbname
        if user is not None and password is not None:
            conn = MongoClient(f'mongodb://{user}:{password}@{host}:{port}/')
        else:
            conn = MongoClient(host, port)
        self._ctx = conn

    def execute(self, query_sql:str):
        """
        Execute SQL in mongodb.

        Args:
            query_sql (str): SQL query statement.
        """
        db = self._ctx[self.dbname]
        query_mongo = create_mongo_shell_query(sql_to_spec(query_sql))

        mongo_data = eval(query_mongo)
        
        return mongo_data





