import re


# STR_NUM_SCALE_TO_NUM = {"billion": 1e9, "million": 1e6, "thousand": 1e3}
# CURR_SIGN_TO_CURR_NAME = {"£": "GBP"}


def convert_string_to_bool(value):
    bool_value = {
        "false": False,
        "f": False,
        "true": True,
        "t": True,
    }.get(value.lower(), None)

    if bool_value is None:
        raise ValueError(
            f"Cannot convert {value} to boolean, acceptable values are {list(bool_value.keys())}"
        )
    return bool_value


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
    print(convert_camel_to_snake_case("someTextToTestHere"))
    print(convert_camel_to_snake_case("_someTextToTestHere"))
