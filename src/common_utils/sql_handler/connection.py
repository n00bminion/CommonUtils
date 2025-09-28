from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

# db module
import sqlite3
import sqlalchemy

# local module
from common_utils.io_handler import file
from common_utils.sql_handler.query import QueryParser


class DatabaseConnection(ABC):
    """
    Use by setting a context manager shown below:

    For sqlite:

    Example:
        with DatabaseConnection(
            database_file_path="path/to/your/file.db",
            connection_engine="sqlite",
        ) as conn:
            conn.select_into_dataframe('select * from your_table')

    Caveat:
        If database doesn't exist then it will be created

    For postgres:

    Example:
        with DatabaseConnection(
            port=5432,
            host='localhost,
            database_name='your_db',
            password='your_password',
            user = 'your_user',
            connection_engine="postgres"
        ) as conn:
            conn.select_into_dataframe('select * from your_table')

    Caveat:
        If database doesn't exist then it will raise an error

    """

    _registry = {}
    _resource_path = "sql_handler/resource"

    def __init_subclass__(cls, connection_engine, **kwargs):
        # register the child classes
        cls._registry[connection_engine] = cls
        return super().__init_subclass__(**kwargs)

    def __new__(cls, connection_engine, **kwargs):
        # generate new class based on connection_engine
        try:
            obj = cls._registry[connection_engine]
            obj.connection_engine = connection_engine
            return super().__new__(obj)
        except KeyError as e:
            raise ValueError(
                f"{connection_engine} is not in list of allowed connection_engines. Allowed values are: {', '.join(cls._registry.keys())}"
            )

    @property
    @abstractmethod
    def database_connection(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.database_connection.close()

    @abstractmethod
    def select_into_dataframe(query, self):
        """
        Select data from a table or view into a pandas dataframe
        Note that query can be sql string or dictionary.

        The dictionary need to be of the form below. Note that filters and columns
        can be {} and [] respectively to indicate no filter were chosen and
        all columns are selected. You can use this if the query is a simple
        select query.

        >>> {
            'table':'table name',
            'columns': ['list','of','column','names'],
            'filters'{
                'column':{
                    'comparator':'value'
                }
            }
        }

        Args:
            query: a sql query string or a dictionary with keys {'table','columns','filters'}.

        Return:
            pandas dataframe
        """
        pass

    @abstractmethod
    def execute_statement(self, query):
        """
        Execute a sql statement.

        Args:
            query: a sql query string

        Return:
            None
        """
        pass

    @abstractmethod
    def insert_into_table(self, dataframe, table_name, if_exixts="append"):
        """
        Insert data from dataframe source table and target table, column names need to match

        >> category = pd.DataFrame([
                            [1,'b','f'],
                            [2,'a','o'],
                            [3,'r','z']
                        ])
        >> category.columns = ['a','b','c']

        >> insert_data_frame_to_sql(category,'Category')

        Args:
            dataframe: pandas dataframe to be insert
            table_name: name of the table the dataframe is inserting into
            if_exists: derive from pandas if_exists argument in pd.to_sql. Default is 'append'

        """
        pass

    @abstractmethod
    def get_all_objects(self):
        """
        Gets a table of all the sql objects

        Return:
            pandas dataframe of all the objects in the database along.
        """
        pass

    @abstractmethod
    def get_table_details(self):
        """
        Gets a table of all the sql objects

        Return:
            pandas dataframe of all the objects in the database along.
        """
        pass


class PostgresConnection(DatabaseConnection, connection_engine="postgres"):

    def __init__(
        self,
        database_name="postgres",
        password="postgres",  # this is sensitive so load from env
        host="localhost",
        port=5432,
        user="postgres",
        *args,
        **kwargs,
    ):
        self.database_name = database_name
        self.password = password
        self.host = host
        self.port = port
        self.user = user

    def __exit__(self, type, value, tb):
        self.database_connection.close()
        self._engine.dispose()

    @property
    def database_connection(self):
        try:
            # https://www.project-open.com/en/howto-postgresql-port-secure-remote-access#:~:text=Open%20Windows%20Firewall%20Port&text=As%20an%20alternative%20you%20can,Specific%20local%20ports%3A%205432

            # using sqlalchemy instead of psycopg2 since pandas throws warning if the conn isn't sqlalchemy
            # return psycopg2.connect(**self.connection_dict)
            self._engine = sqlalchemy.create_engine(
                f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"
            )
            return self._engine.connect()
        except Exception as e:
            raise e

    @QueryParser
    def select_into_dataframe(self, query):
        return pd.read_sql_query(query, self.database_connection)

    @QueryParser
    def execute_statement(self, query):
        try:
            with self.database_connection.begin():
                # not able to execute script like sqlite :(
                self.database_connection.execute(query)
        except Exception as e:
            raise e

    def insert_into_table(self, dataframe, table_name, if_exixts="append", **kwargs):

        assert isinstance(dataframe, pd.DataFrame), "Use dataframe as data source"

        dataframe.to_sql(
            name=table_name,
            con=self.database_connection,
            index=False,
            if_exists=if_exixts,
            **kwargs,
        )

    def get_all_objects(self):
        sql = file._read_internal_resource(
            f"{self._resource_path}/{self.connection_engine}/get_all_objects.sql"
        )
        return self.select_into_dataframe(
            sql,
        )

    def get_table_details(self, table_name, schema_name):
        sql = file._read_internal_resource(
            f"{self._resource_path}/{self.connection_engine}/get_object_details.sql"
        ).format(
            schema=schema_name,
            table_name=table_name,
        )
        return self.select_into_dataframe(
            sql,
        )


class SqliteConnection(DatabaseConnection, connection_engine="sqlite"):

    def __init__(
        self,
        database_file_path="database.db",
        *args,
        **kwargs,
    ):
        self.database_file_path = file.prepare_file_path(Path(database_file_path))

    @property
    def database_connection(self):
        try:
            return sqlite3.connect(self.database_file_path)
        except Exception as e:
            raise e

    @QueryParser
    def select_into_dataframe(self, query):
        return pd.read_sql_query(query, self.database_connection)

    @QueryParser
    def execute_statement(self, query):
        with self.database_connection as conn:
            # A Connection object can be used as a context manager that automatically commits or rolls back open transactions when leaving the body of the context manager.
            # If the body of the with statement finishes without exceptions, the transaction is committed.
            # If this commit fails, or if the body of the with statement raises an uncaught exception, the transaction is rolled back
            conn.executescript(query)
            # cursor.commit()

    def insert_into_table(self, dataframe, table_name, if_exixts="append"):
        assert isinstance(dataframe, pd.DataFrame), "Use dataframe as data source"
        dataframe.to_sql(
            name=table_name,
            con=self.database_connection,
            index=False,
            if_exists=if_exixts,
        )

    def get_all_objects(self):
        sql = file._read_internal_resource(
            f"{self._resource_path}/{self.connection_engine}/get_all_objects.sql"
        )
        return self.select_into_dataframe(sql)

    def get_table_details(self, table_name):

        sql = file._read_internal_resource(
            f"{self._resource_path}/{self.connection_engine}/get_object_details.sql"
        ).format(
            table_name=table_name,
        )
        return self.select_into_dataframe(
            sql,
        )
