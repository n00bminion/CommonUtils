import re


def _convert_camel(camel_text, replacement):
    camel_search_pattern = "(?<!^)(?=[A-Z])"
    possible_duped_pattern = re.sub(
        camel_search_pattern, replacement, camel_text
    ).lower()
    return possible_duped_pattern.sub(rf"\{replacement}+", f"{replacement}", camel_text)


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
    convert_camel_to_snake_case("someTextToTestHere")
