import re
from common_utils.data_handler.audit import DEFAULT_AUDIT_COLUMNS


def _sanitise_parameters(
    table_name, staging_table_name, matching_columns, nonmatching_columns
):
    """
    Private function to help sanitise functions in this module, not for external use.
    """
    if not staging_table_name:
        staging_table_name = get_staging_table_name(table_name)

    assert isinstance(matching_columns, list), (
        f"matching_columns should either be a tuple or list but got {type(matching_columns)} instead"
    )

    assert isinstance(nonmatching_columns, list), (
        f"nonmatching_columns should either be a tuple or list but got {type(nonmatching_columns)} instead"
    )

    return staging_table_name, matching_columns, nonmatching_columns


def get_staging_table_name(table_name):
    """
    Autogenerate staging table name. This enforces staging table name format.

    Args:
        table_name (str): name of the table

    Returns:
        staging_table_name: name of the staging table
    """
    # replace square brackets if any
    return f"{re.sub(r'\[|\]', '', table_name)}_staging"


def update_staging_table_status(
    database_connection,
    table_name: str,
    matching_columns: list,
    nonmatching_columns: list,
    staging_table_name: str = None,
):
    """
    Identify records in staging table and update the status column with the appropriate status.
    Status is either:
    - "new" - new records to be added
    - "update" - old records to be updated with the new data

    Args:
        database_connection : database connection object
        table_name (str): name of table
        matching_columns (list | tuple): columns that are in both staging table and table. These columns determine if the records will be added/updated.
        nonmatching_columns (list | tuple): columns that are in both staging table and table. These columns are not used to determine if the records will be added/updated.
        staging_table_name (str, optional): name of staging table. Defaults to None to use "get_staging_table_name" function to automatically derive the staging table name (This is the preferred method)

    """

    staging_table_name, matching_columns, nonmatching_columns = _sanitise_parameters(
        table_name, staging_table_name, matching_columns, nonmatching_columns
    )

    matching_str_columns = " and ".join(
        [f"stg.{column} = dlt.{column}" for column in matching_columns]
    )

    nonmatching_str_columns = " and ".join(
        [f"stg.{column} != tgt.{column}" for column in nonmatching_columns]
    )

    for step, query in {
        # identify the new records if any
        "Setting new records status to 'new'": f"""
            update {staging_table_name} as stg
                set status = 'new'
                from 
                (
                    select {", ".join(matching_columns)} 
                    from {staging_table_name}
                    except
                    select {", ".join(matching_columns)} 
                    from {table_name}
                ) as dlt
                where {matching_str_columns}
        """,
        # otherwise update the rest of the records
        "Setting old records with updated data status to 'update'": f"""
            update {staging_table_name} as stg
            set stg.status = 'update'
            from {table_name} src
            where stg.status != 'new'
            and {matching_str_columns.replace("dlt", "src")}  
            and {nonmatching_str_columns}
        """,
        "Setting leftover old records status to 'old'": f"""
            update {staging_table_name}
            set status = 'old'
            where status not in ('new','update')
        """,
    }.items():
        database_connection.execute_statement(query)
        print(f"{step} in {staging_table_name}")


def sync_staging_table_to_source_table(
    database_connection,
    table_name: str,
    matching_columns: list | tuple,
    nonmatching_columns: list | tuple,
    staging_table_name: str = None,
    audit_columns: list = None,
):
    """
    Load new records or update records in source table using staging table

    Args:
        database_connection : database connection object
        table_name (str): name of table
        matching_columns (list | tuple): columns that are in both staging table and table. These columns determine if the records will be added/updated.
        nonmatching_columns (list | tuple): columns that are in both staging table and table. These columns are not used to determine if the records will be added/updated.
        staging_table_name (str, optional): name of staging table. Defaults to None to use "get_staging_table_name" function to automatically derive the staging table name (This is the preferred method)
        audit_columns (list): list of audit columns. Defaults to None to use the pre-set columns (DEFAULT_AUDIT_COLUMNS) from common_utils.data_handler.audit

    """
    staging_table_name, matching_columns, nonmatching_columns = _sanitise_parameters(
        table_name, staging_table_name, matching_columns, nonmatching_columns
    )

    if not audit_columns:
        audit_columns = list(DEFAULT_AUDIT_COLUMNS.keys())

    all_columns = matching_columns + nonmatching_columns + audit_columns
    sql_str_columns = ", ".join(all_columns)

    update_columns = ", ".join(
        [f"tgt.{column} = stg.{column}" for column in all_columns]
    )

    matching_str_columns = " and ".join(
        [f"tgt.{column} = stg.{column}" for column in matching_columns]
    )

    for step, query in {
        "Inserting new records": f"""
            insert into {table_name} ({sql_str_columns})
            select {sql_str_columns}
            from {staging_table_name}
            where status = 'new'
        """,
        "Updating old records": f"""
            update {table_name} as tgt
            set {update_columns}
            from {staging_table_name} stg
            where status = 'update'
            and {matching_str_columns}
        """,
    }.items():
        database_connection.execute_statement(query)
        print(f"{step} in {table_name}")


def is_new_data_available(
    database_connection,
    table_name: str,
    staging_table_name: str = None,
):
    if not staging_table_name:
        staging_table_name = get_staging_table_name(table_name)

    return (
        database_connection.select_into_dataframe(
            f"""
            SELECT COUNT(*) data_count
            FROM {staging_table_name}
            WHERE status in ('new','update')
        """
        )["data_count"].item()
        > 0
    )


if __name__ == "__main__":
    print(get_staging_table_name("[schema].abc"))
