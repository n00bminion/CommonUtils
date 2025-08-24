from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

# db module
import sqlite3
import sqlalchemy

# local module
from common_utils import file_handler
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

    def __init_subclass__(cls, connection_engine, **kwargs):
        # register the child classes
        cls._registry[connection_engine] = cls
        return super().__init_subclass__(**kwargs)

    def __new__(cls, connection_engine, **kwargs):
        # generate new class based on connection_engine
        try:
            obj = cls._registry[connection_engine]
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
    def select_into_dataframe(self):
        pass

    @abstractmethod
    def execute_statement(self):
        pass

    @abstractmethod
    def insert_into_table(self):
        """
        Insert data from dataframe source table and SQLite target table, column names need to match

        category = pd.DataFrame([
                            [1,'b','f'],
                            [2,'a','o'],
                            [3,'r','z']
                        ])
        category.columns = ['a','b','c']

        insert_data_frame_to_sql(category,'Category')
        """
        pass

    @abstractmethod
    def get_all_objects(self):
        pass

    @abstractmethod
    def get_table_details(self):
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

    def insert_into_table(self, dataframe, table_name, if_exixts="append"):

        assert isinstance(dataframe, pd.DataFrame), "Use dataframe as data source"

        dataframe.to_sql(
            name=table_name,
            con=self.database_connection,
            index=False,
            if_exists=if_exixts,
        )

    _ALL_OBJECT_QUERY = """
        select
            n.nspname as schema_name
            ,c.relname as object_name
            ,r.rolname as object_owner
            ,case c.relkind
                when 'r' then 'TABLE'
                when 'm' then 'MATERIALIZED_VIEW'
                when 'i' then 'INDEX'
                when 'S' then 'SEQUENCE'
                when 'v' then 'VIEW'
                when 'c' then 'TYPE'
                else c.relkind::text
            end as object_type
        from pg_class c
        join pg_roles r
        on r.oid = c.relowner
        join pg_namespace n
        on n.oid = c.relnamespace
        where n.nspname not in ('information_schema', 'pg_catalog')
            and n.nspname not like 'pg_toast%'
        order by n.nspname, c.relname;
    """

    def get_all_objects(self):
        self.select_into_dataframe(self._ALL_OBJECT_QUERY)

    _OBJECT_DETAILS = """
        SELECT attrelid::regclass AS tbl
        , attname            AS col
        , atttypid::regtype  AS datatype
        -- more attributes?
        FROM   pg_attribute
        WHERE  attrelid = '{schema}.{table}'::regclass  -- table name optionally schema-qualified
        AND    attnum > 0
        AND    NOT attisdropped
        ORDER  BY attnum;
    """

    def get_table_details(self, table, schema="public"):
        return self.select_into_dataframe(
            self._OBJECT_DETAILS.format(
                schema=schema,
                table=table,
            )
        )


class SqliteConnection(DatabaseConnection, connection_engine="sqlite"):

    def __init__(
        self,
        database_file_path="database.db",
        *args,
        **kwargs,
    ):
        self.database_file_path = file_handler.prepare_file_path(
            Path(database_file_path)
        )

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

    _ALL_TABLE_QUERY = (
        "SELECT * "
        "FROM sqlite_master "
        "WHERE type IN ('table','view') "
        "ORDER BY name"
    )

    def get_all_objects(self):
        return self.select_into_dataframe(self._ALL_TABLE_QUERY)

    _OBJECT_DETAILS = "SELECT * FROM PRAGMA_TABLE_INFO( '{table_name}' )"

    def get_table_details(self, table_name):
        return self.select_into_dataframe(
            self._OBJECT_DETAILS.format(table_name=table_name)
        )
