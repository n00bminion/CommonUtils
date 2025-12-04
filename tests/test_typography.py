import pytest
from common_utils.format_handler import typography


def test_convert_string_to_bool_known_values():
    # The module maps known keys; ensure known keys return a boolean or raise appropriately
    assert isinstance(typography.convert_string_to_bool("false"), bool)
    assert isinstance(typography.convert_string_to_bool("f"), bool)


def test_convert_large_number_str_to_numeric_scalar():
    assert typography.convert_large_number_str_to_numeric_scalar("million") == 1e6


def test_convert_large_number_unknown_without_default_raises():
    with pytest.raises(ValueError):
        typography.convert_large_number_str_to_numeric_scalar("nonesuch")


def test_convert_large_number_with_default():
    assert (
        typography.convert_large_number_str_to_numeric_scalar(
            "nonesuch", return_value_when_fail=1
        )
        == 1
    )


def test_camel_snake_kebab_and_pascal():
    assert typography.convert_camel_to_snake_case("someText") == "some_text"
    assert typography.convert_snake_to_camel_case("some_text") == "SomeText"
    assert typography.convert_camel_to_kebab_case("someText") == "some-text"
    with pytest.raises(NotImplementedError):
        typography.convert_pascal_to_snake_case("SomeText")
