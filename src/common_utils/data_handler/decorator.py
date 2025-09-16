import pandas as pd
import socket


def add_created_audit_columns(*outer_args, add_created_date=True, add_created_by=True):
    """
    Decorator to add _CreatedDate and _CreatedBy column to dataframe automatically.
    Can set add_created_date and/or add_created_by to False to not add the columns

    Args:
        add_created_date: default set to True
        add_created_by: default set to True

    Return:
        pandas DataFrame

    """
    if (len(outer_args)) > 1:
        raise SyntaxError(
            "add_created_audit_columns function only allow for 1 positional argument. "
            "The rest must be keyword arguements"
        )

    def _add_created_date(data):
        return data.assign(_CreatedDate=pd.Timestamp.now())

    def _add_created_by(data):
        return data.assign(_CreatedBy=socket.gethostname())

    # default everything (no params passed)
    if len(outer_args) == 1:
        function = outer_args[0]
        if callable(outer_args[0]):

            def _(*args, **kwargs):
                data = function(*args, **kwargs)
                data = _add_created_by(data)
                data = _add_created_date(data)
                return data

        else:
            raise SyntaxError(
                "add_created_audit_columns only take the decorated function as 1st positional argument. "
                f"{function} is not a function (not callable) and is of type {type(function)}"
            )

    else:

        def _(function):
            def __(*args, **kwargs):
                data = function(*args, **kwargs)

                if add_created_date:
                    data = _add_created_date(data)

                if add_created_by:
                    data = _add_created_by(data)

                return data

            return __

    return _


if __name__ == "__main__":

    @add_created_audit_columns(add_created_by=False)
    def test():
        return pd.DataFrame({"a": [1, 2, 3]})

    print(test())
