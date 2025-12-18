import tempfile
import shutil
from pathlib import Path
import pandas as pd
from common_utils.io_handler.database.connection import DatabaseConnection


def test_sqlite_connection_create_insert_select():
    # create a temporary directory under the user's home so prepare_file_path accepts it
    tmpdir = Path(tempfile.mkdtemp(dir=Path.home()))
    try:
        db_file = tmpdir / "test_db.sqlite"

        # Create connection using the DatabaseConnection factory with connection_engine="sqlite"
        with DatabaseConnection(
            connection_engine="sqlite", database_file_path=str(db_file)
        ) as conn:
            # create table
            conn.execute_statement("CREATE TABLE test_table (id INTEGER, val TEXT);")

            # insert via pandas DataFrame
            df_in = pd.DataFrame([{"id": 1, "val": "a"}, {"id": 2, "val": "b"}])
            conn.insert_into_table(df_in, "test_table")

            # select all using SQL string
            df_out = conn.select_into_dataframe("SELECT id, val FROM test_table")
            assert len(df_out) == 2
            assert set(df_out["val"]) == {"a", "b"}

            # select using dict-style query (columns empty => all)
            q = {"table": "test_table", "columns": [], "filters": {}}
            df_out2 = conn.select_into_dataframe(q)
            assert len(df_out2) == 2

            # select with a comparator filter via dict to avoid list-join pitfalls
            q2 = {
                "table": "test_table",
                "columns": ["id", "val"],
                "filters": {"id": {">": 1}},
            }
            df_out3 = conn.select_into_dataframe(q2)
            assert len(df_out3) == 1
            assert df_out3["val"].iloc[0] == "b"

    finally:
        # cleanup
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
