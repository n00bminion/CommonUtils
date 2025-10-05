def store_data(database_connection, data, table_name, **kwargs):
    database_connection.insert_into_table(
        dataframe=data, table_name=table_name, **kwargs
    )


def get_stored_data(database_connection, table_name, columns=None, filters=None):
    return database_connection.select_into_dataframe(
        dict(table=table_name, columns=columns or [], filters=filters or {})
    )
