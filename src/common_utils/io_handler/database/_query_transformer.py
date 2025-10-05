from functools import singledispatch


# dodgy black formatting so turning formatting off here
# fmt: off
@singledispatch
def _transform_kv_to_clause(filter, column):
    raise NotImplementedError(
        f"Unable to transform value {filter} for column '{column}'. The type {type(filter)} is not supported"
    )

@_transform_kv_to_clause.register(str)
def _str(filter, column):
    return f"{column} = '{filter}'"

@_transform_kv_to_clause.register(int)
@_transform_kv_to_clause.register(float)
def _num(filter, column):
    return f"{column} = {filter}"


@_transform_kv_to_clause.register(list)
@_transform_kv_to_clause.register(tuple)
def _iter(filter, column):
    reformatted_filter = [
        (
            element
            # if int then we just leave it as is
            if type(element) == int
            # otherwise we wrap quotes around it to signify it's str
            else f"'{element}'"
        )
        for element in filter
    ]
    return f"{column} in " f"({ ', '.join(reformatted_filter) })"

@_transform_kv_to_clause.register(dict)
def _dict(filter, column):
    sql_comparator = {">", ">=", "<", "<=", "=", "!=", "<>"}

    non_str_comparator = [
        comparator for comparator in filter.keys() if type(column) != str
    ]
    assert (
        len(non_str_comparator) == 0
    ), f"Keys in {filter} represent comparators and should be of type str"

    # difference between 2 sets
    rogue_comparator = filter.keys() - sql_comparator
    assert len(rogue_comparator) == 0, f"{rogue_comparator} sql comparator(s) are not allowed. Allowed comparators are {sql_comparator}"

    # I should probably check the value here but cbb
    return [f"{column} {comparator} {value}" for comparator, value in filter.items()]
# fmt: on


if __name__ == "__main__":
    x = _transform_kv_to_clause("a", "b")
    x
