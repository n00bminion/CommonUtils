import sqlite3
import pandas as pd
import os
from pathlib import Path


def _connect_to_db(database_path, database_file):
    """
    Function to point to a DB file and access its content
    (will also generate DB file if not exists)

    """
    ## if the path exists, connection will
    assert database_file, "Must include db file name"

    if os.path.isdir(database_path):
        return sqlite3.connect(Path(database_path, database_file))


def _truncate_table_conditional_parser(conditional):
    """
    Function to parse the conditional
    paramter for function the SQL.truncate_table()
    """
    col_val = [
        (" AND " + i[0] + " IN (")
        + (
            "'" + "','".join(i[1]) + "')"
            if isinstance(i[1], list)
            else "'" + i[1] + "')"
        )
        for i in list(conditional.items())
    ]
    ## remove the first 'and '
    return "WHERE" + "".join(col_val)[4:]


def select_into_dataframe(
    query,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """
    Pass "select" query as argument and returns
    data in a DataFrame. Here's a simple example:

    ''' select * from sqlite_master '''

    """
    conn = _connect_to_db(database_path, database_file)
    assert bool(conn), "DB file directory doesn't exist"
    df = pd.read_sql_query(str(query), conn)
    conn.close()
    return df


def exec_sql_uery(
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
    assert bool(conn), "DB file directory doesn't exist"
    conn.cursor().executescript(str(query))
    conn.commit()
    conn.close()


def insert_data_frame_to_sql(
    dataframe,
    table_name,
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
    dataframe.to_sql(name=table_name, con=conn, index=False, if_exists=if_exists)


def truncate_table(
    table_name,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
    conditional=None,
):
    """
    Clear out/truncate the table
    Leave condition param empty if you want
    to truncate the whole table else pass through
    a dictionary with key being the column
    and the values as list of the items
    in the row that you would like to delete from

    Parameter
        table_name <<str>>
        comditional <<dict>>

    Example
        conditional = {
            'symbol':['TSLA','AAPL','RBLX'],
            'country':'United States',
        }
        truncate_table('freetrade_security_raw',conditional)
    """
    conditional = (
        "" if conditional == None else _truncate_table_conditional_parser(conditional)
    )
    query = " DELETE FROM {} {}".format(table_name, conditional)
    exec_sql_uery(query, database_path, database_file)


def list_sql_objects(
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """Return a list table of a objects in the DB"""
    return [
        i
        for i in select_into_dataframe(
            """ SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name""",
            database_path,
            database_file,
        ).name
    ]


def get_sql_columns(
    table_name,
    database_path=os.getcwd(),
    database_file=os.getenv("database_file"),
):
    """Return a list of columns for the required table"""
    assert isinstance(table_name, str), "table_name needs to a string"
    return [
        i
        for i in select_into_dataframe(
            """ SELECT * FROM {} limit 0""".format(table_name),
            database_path,
            database_file,
        ).columns
    ]
