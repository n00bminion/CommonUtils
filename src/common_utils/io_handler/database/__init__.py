from common_utils.database.connection import DatabaseConnection

if __name__ == "__main__":
    with DatabaseConnection(
        database_file_path="test.db",
        connection_engine="sqlite",
    ) as conn:
        conn.execute_statement("create table test_table (id int)")

        df = conn.select_into_dataframe(
            {
                "table": "test_table",
                "columns": [],
                "filters": {"id": ["1"]},
            }
        )

        df
