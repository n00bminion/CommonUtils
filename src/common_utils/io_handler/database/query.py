from functools import partial, singledispatchmethod
import inspect
import re
import sqlparse

from common_utils.io_handler.database._query_transformer import _transform_kv_to_clause


class QueryParser:
    """
    Class decorator to pre-check sql queries/dictionary passed into the database connection objects
    """

    def __init__(self, function):
        self.function = function
        self._expected_arguement = "query"
        self._sqlparse_kwargs = dict(
            keyword_case="upper",
            use_space_around_operators=True,
            reindent=True,
            reindent_aligned=True,
        )

    def __call__(self, *args, **kwargs):
        all_arguments_name = inspect.signature(self.function).parameters.keys()

        if self._expected_arguement not in all_arguments_name:
            raise KeyError(
                f"{self._expected_arguement} is expected to be an argument but {self.function} does't have this argument"
            )

        # if query is in keyword args then we parse it and replace its value
        if self._expected_arguement in kwargs:
            kwargs[self._expected_arguement] = self.parse(kwargs["query"])
            result = self.function(*args, **kwargs)

        # if query is in positional args, we can deduce the position of "query"
        # which should be in the same the position in the args
        index_position = list(all_arguments_name).index(self._expected_arguement)
        # convert tuple to list to allow reassignment
        args = list(args)
        args[index_position] = self.parse(args[index_position])
        result = self.function(*args, **kwargs)

        return result

    #  method to allow class to be a decorator
    #  https://stackoverflow.com/questions/30104047/how-can-i-decorate-an-instance-method-with-a-decorator-class
    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    @singledispatchmethod
    def parse(self, query):
        raise NotImplementedError(f"Unable to parse query type: {type(query)}")

    @parse.register
    def _parse_string(self, query: str):
        return sqlparse.format(
            re.sub(
                # remove double whitespace in between
                r"\s{2,}",
                " ",
                # strip leading and trailing whitespaces
                query.strip(),
            ),
            **self._sqlparse_kwargs,
        )

    # using dictionary to filter simple query rather
    @parse.register
    def _parse_dict(self, query: dict):
        # top level should have just 2 keys, table and filter
        table = "table"
        columns = "columns"
        filters = "filters"
        allowed_key = [table, columns, filters]

        # check if all the keys are there, even if "select * ", still expects filter to be an empty dict
        assert sorted(list(query)) == (sorted(allowed_key)), (
            f"Only a dictionary with {len(allowed_key)} keys is allowed. The keys are {allowed_key}. The passed in keys are {list(query)}"
        )

        # table name is only allowed to be a string
        table_name = query[table]
        assert isinstance(table_name, str), (
            f"The value for {table} is {table_name}. This is expected to be a str but instead got {type(table_name)}"
        )

        # need to pass in list or tuple of columns
        columns_iter = query[columns]
        assert isinstance(columns_iter, (list, tuple)), (
            f"The value for {columns} is {columns_iter}. This is expected to be a list or tuple but instead got {type(columns_iter)}. If choosing all columns, use an empty list or tuple"
        )

        # expect dictionary for filter
        filter_dict = query[filters]
        assert isinstance(filter_dict, dict), (
            f"The value for {filters} is {filter_dict}. This is expected to be a dict but instead got {type(filter_dict)}. If there's no filtering, use an empty dict"
        )

        # from this point on, we can construct query
        select_columns_from_table = f"SELECT {', '.join(columns_iter) if columns_iter else '*'} FROM  {table_name}"

        if not filter_dict:
            # return if no filtering
            return sqlparse.format(
                select_columns_from_table,
                **self._sqlparse_kwargs,
            )

        # all the keys in this nested filter dict represent columns and need to be str also
        non_str_columns = [
            column for column in filter_dict.keys() if not isinstance(column, str)
        ]
        assert len(non_str_columns) == 0, (
            f"Keys in {filter} represent column names and should be of type str"
        )

        # transform the filter into actual list of sql clauses

        sql_clause_list = [
            _transform_kv_to_clause(filter_clause, column)
            for column, filter_clause in filter_dict.items()
        ]

        for index, clause in enumerate(sql_clause_list):
            if isinstance(clause, str):
                sql_clause_list[index] = f" AND {clause}"
            elif isinstance(clause, list):
                sql_clause_list[index] = " AND ".join(clause)

        final_query = select_columns_from_table + " WHERE " + " ".join(sql_clause_list)

        where_and_pattern = r"\bwhere\s+and\b"
        if re.search(where_and_pattern, final_query, re.IGNORECASE):
            final_query = re.sub(
                pattern=where_and_pattern,
                repl="WHERE ",
                string=final_query,
                flags=re.IGNORECASE,
            )

        return sqlparse.format(
            final_query,
            **self._sqlparse_kwargs,
        )
