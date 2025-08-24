from functools import partial, singledispatchmethod
import inspect
import re
import sqlparse


class QueryParser:
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

    # https://stackoverflow.com/questions/30104047/how-can-i-decorate-an-instance-method-with-a-decorator-class
    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    @singledispatchmethod
    def parse(self, query):
        raise NotImplementedError(f"Unable to parse query type: {type(query)}")

    # let's just stick to sql string, dictionary is wayyyyyyy to complicated for this
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
