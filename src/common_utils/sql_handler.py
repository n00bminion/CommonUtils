import sqlite3
import pandas as pd
import os
from pathlib import Path


def _default_select(table, conditional):
    return f" SELECT * FROM {table} {conditional}"


def _connect_to_db(database_path, database_file):
    """
    Function to point to a DB file and access its content
    (will also generate DB file if not exists)

    """
    ## if the path exists, connection will
    assert database_file, "Must include db file name"

    if os.path.isdir(database_path):
        return sqlite3.connect(Path(database_path, database_file))


def _conditional_parser(conditionals):
    """
    Function to parse the conditional
    paramter for function the SQL.truncate_table()
    """

    if conditionals == {}:
        return ""

    def _parse(column, conditional):

        prefix = f" AND {column}"

        if isinstance(conditional, dict):

            if not len(conditional):
                return ""

            dict_conditional = []
            for key, value in conditional.items():

                if isinstance(value, str):
                    value = f"'{value}'"

                dict_conditional.append(f"{prefix} {key} {value}")

                return " ".join(dict_conditional)

        if isinstance(conditional, list):
            if all((isinstance(item, int) for item in conditional)):
                f'{prefix} IN ({",".join(map(str, conditional))})'

            return f"{prefix} IN ('{"','".join(conditional)}')"

        if isinstance(conditional, int):
            return f"{prefix} = {conditional}"

        return f"{prefix} = '{conditional}'"

    ## remove the first 'and '
    return (
        "WHERE"
        + "".join(
            [
                _parse(column, conditional)
                for column, conditional in conditionals.items()
            ]
        )[4:]
    )


def select_into_dataframe(
    query=None,
    table=None,
    conditional=None,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """
    Pass "select" query as argument and returns
    data in a DataFrame. Here's a simple example:

    ''' select * from sqlite_master '''

    """
    conn = _connect_to_db(database_path, database_file)
    if table and (conditional is not None) and not query:
        query = _default_select(table, conditional)

    if not query:
        raise Exception(f"query and/or {table=} and {conditional=} was not supplied")

    df = pd.read_sql_query(str(query), conn)

    conn.close()
    return df


def exec_sql_query(
    query,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """
    Used to execute query in the SQLite DB (i.e. Create table, drop table etc.).
    Below is an example, 1st query creating a test table and 2nd query is to drop test table (copy and try it out):

    - Create a new table
    '''CREATE TABLE IF NOT EXISTS test_table (id integer PRIMARY KEY, name text , begin_date text, end_date text);'''

    - Dropping a table
    '''DROP TABLE IF EXISTS test_table;'''

    """
    conn = _connect_to_db(database_path, database_file)
    conn.cursor().executescript(str(query))
    conn.commit()
    conn.close()


def insert_data_frame_to_sql(
    dataframe,
    table,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
    if_exists="append",
):
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
    conn = _connect_to_db(database_path, database_file)
    assert isinstance(dataframe, pd.DataFrame), "Use dataframe as data source"
    dataframe.to_sql(name=table, con=conn, index=False, if_exists=if_exists)


def truncate_table(
    table,
    conditional=None,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """
    Clear out/truncate the table
    Leave condition param empty if you want
    to truncate the whole table else pass through
    a dictionary with key being the column
    and the values as list of the items
    in the row that you would like to delete from

    Parameter
        table <<str>>
        comditional <<dict>>

    Example
        conditional = {
            'symbol':['TSLA','AAPL','RBLX'],
            'country':'United States',
        }
        truncate_table('freetrade_security_raw',conditional)
    """
    conditional = "" if conditional == None else _conditional_parser(conditional)
    query = " DELETE FROM {} {}".format(table, conditional)
    exec_sql_query(query, database_path, database_file)


def list_sql_objects(
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """Return a list table of a objects in the DB"""
    return [
        i
        for i in select_into_dataframe(
            query=" SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name",
            database_path=database_path,
            database_file=database_file,
        ).name
    ]


def get_sql_columns(
    table,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """Return a list of columns for the required table"""
    assert isinstance(table, str), "table needs to a string"
    return [
        i
        for i in select_into_dataframe(
            query=f"SELECT * FROM {table} limit 0",
            database_path=database_path,
            database_file=database_file,
        ).columns
    ]
