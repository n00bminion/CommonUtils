import re


_STR_TO_BOOL_MAPPING = {
    **{value: False for value in ("false", "f")},
    **{value: False for value in ("true", "t")},
}

_STR_NUM_SCALE_TO_NUM = {
    **{value: 1e12 for value in ("trillion", "t", "tn")},
    **{value: 1e9 for value in ("billion", "b", "bn")},
    **{
        value: 1e6 for value in ("million", "m", "mn", "mill", "mln", "g")
    },  # g is a bit dodgy?
    **{
        value: 1e3
        for value in (
            "thousand",
            "k",
        )
    },
}


def _get_from_global_dict(value, global_dict):
    try:
        derived_value = global_dict[value.lower()]
    except KeyError:
        raise ValueError(
            f"Cannot convert {value} to boolean, acceptable values are {list(global_dict.keys())}"
        )
    return derived_value


def convert_large_number_str_to_numeric_scalar(value, return_value_when_fail=None):
    try:
        return _get_from_global_dict(value=value, global_dict=_STR_NUM_SCALE_TO_NUM)
    except ValueError:
        if return_value_when_fail is None:
            raise ValueError(
                f"Unable to convert {value} to a numeric scalar, there are 2 options to proceed:\n"
                "1. Set the 'return_value_when_fail' parameter (to 1 maybe?) to allow a default value to be returned.\n"
                "2. Update the global variable '_STR_NUM_SCALE_TO_NUM' in common_utils/format_handler/typography to account for the new mapping."
            )
        return return_value_when_fail


def convert_string_to_bool(value):
    return _get_from_global_dict(value=value, global_dict=_STR_TO_BOOL_MAPPING)


def _convert_camel(camel_text, replacement):
    camel_search_pattern = "(?<!^)(?=[A-Z])"
    possible_duped_pattern = re.sub(
        camel_search_pattern, replacement, camel_text
    ).lower()
    return re.sub(rf"\{replacement}+", f"{replacement}", possible_duped_pattern)


def convert_camel_to_snake_case(text):
    return _convert_camel(text, "_")


def convert_snake_to_camel_case(text):
    text_list = text.split("_")
    if len(text_list) == 1:
        return text
    return "".join([word.title() for word in text.split("_") if word])


def convert_camel_to_kebab_case(text):
    return _convert_camel(text, "-")


def convert_pascal_to_snake_case(text):
    raise NotImplementedError(
        "Converting pascal case to snake case is not yet available"
    )


if __name__ == "__main__":
    # print(convert_camel_to_snake_case("someTextToTestHere"))
    # print(convert_camel_to_snake_case("_someTextToTestHere"))

    print(convert_large_number_str_to_numeric_scalar("qewas", return_value_when_fail=1))
