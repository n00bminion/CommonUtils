from bs4 import BeautifulSoup
import pandas as pd
from common_utils.io_handler.external import get_request
from common_utils.data_handler.array import chunk_iter
from common_utils.format_handler.typography import convert_camel_to_snake_case
from common_utils.cache_handler.file_cache import cache_to_file
from common_utils.io_handler.file import _read_internal_resource


@cache_to_file(days_to_keep=30)
def _get_global_currency_mapping():
    number_of_column = 6
    raw_mapping = get_request(r"https://www.xe.com/symbols/")
    rows = list(
        chunk_iter(
            #  these are cells in the table (list of cells)
            BeautifulSoup(raw_mapping.content, "html.parser").find_all(
                "div", class_="sc-9436afbc-9 dTLqcL"
            ),
            number_of_column,
        )
    )

    columns = [
        convert_camel_to_snake_case(
            col.text.strip().replace(":", " ").title().replace(" ", "")
        )
        for col in rows[0]
    ]

    fx_mapping = pd.DataFrame(rows[1:], columns=columns).map(lambda x: x.text.strip())
    fx_mapping = (
        fx_mapping.drop(columns=["unicode_decimal", "unicode_hex"])
        .join(fx_mapping.unicode_decimal.str.split(",").explode().str.strip())
        .join(fx_mapping.unicode_hex.str.split(",").explode().str.strip())
        .reset_index(drop=True)
    )

    fx_mapping = fx_mapping.assign(
        country=fx_mapping.country_and_currency.str.split(" ").str[:-1].str.join(" "),
        currency=fx_mapping.country_and_currency.str.split(" ").str[-1],
    )
    relative_root_path = r"format_handler\resource\currency"

    country_currency_fix = pd.DataFrame(
        # currencies to be manually fixed can be found in the resource/currency dir
        _read_internal_resource(rf"{relative_root_path}\country_currency_fix.yaml")
    ).T.reset_index(names=["country_and_currency"])

    fx_mapping = fx_mapping.merge(
        country_currency_fix,
        how="left",
        on="country_and_currency",
        suffixes=("_current", "_fix"),
    )

    fx_mapping = fx_mapping.assign(
        currency=fx_mapping.currency_fix.combine_first(fx_mapping.currency_current),
        country=fx_mapping.country_fix.combine_first(fx_mapping.country_current),
        primary_currency=fx_mapping.country_and_currency.isin(
            # primary currency to be flagged in the data
            _read_internal_resource(rf"{relative_root_path}\primary_currencies.yaml")
        ),
        unicode_decimal=fx_mapping.unicode_decimal.astype(str) + ";",
        unicode_hex="x" + fx_mapping.unicode_hex.astype(str) + ";",
    ).drop(
        columns=["country_current", "currency_current", "country_fix", "currency_fix"]
    )

    return fx_mapping


_GLOBAL_CURRENCY_MAPPING = _get_global_currency_mapping()


def derive_currency_code(value: str, is_primary_currency=True, country=None):
    """
    Function to derive the ISO currency code for a given symbol or unicode

    Args:
        value: string value of a symbol or unicode
        is_primary_currency: control whether to use the smaller subset of the mappings for large currencies only. This is default to True. The subset can be found at \format_handler\resource\currency\primary_currencies.yaml
        country: default to None but can help narrowing down the derivation of currency code if multiple mappings are found

    Returns:
        currency code string
    """
    assert isinstance(value, str), (
        f"Expect value ({value}) passed in to be a string, instead got type {type(value)}"
    )

    value = value.strip()

    if is_primary_currency:
        mappings = _GLOBAL_CURRENCY_MAPPING[_GLOBAL_CURRENCY_MAPPING.primary_currency]
    else:
        mappings = _GLOBAL_CURRENCY_MAPPING

    def _filter_mappings_by_value(mappings, column, value, country):
        currency_code_records = mappings[
            mappings[column] == (value if not value.startswith("&#") else value[2:])
        ][["currency_code", "country"]].drop_duplicates()

        # if multiple mappings, throw exception to use country as well
        if len(currency_code_records) > 1:
            if country:
                currency_code_records = currency_code_records[
                    currency_code_records.country.str.lower().str.strip()
                    == str(country).lower().strip()
                ]
            else:
                raise LookupError(
                    f"Multiple mappings found for {value =}. Try using 'country' parameter to help narrowing down further. "
                    f"Countries found for the multiple mappings are {currency_code_records.country.to_list()}"
                )
        # if no records then throw error cause we can't map
        if currency_code_records.empty:
            raise LookupError(
                f"Currency code not found for {value =}"
                if not country
                else f"Currency code not found for {value =} and {country =}"
            )

        # finally we get the value
        currency_code = currency_code_records.currency_code.values[0]

        return currency_code

    # unicode stuff
    if value.startswith("&#"):
        for column in "unicode_decimal", "unicode_hex":
            return _filter_mappings_by_value(mappings, column, value, country)
    else:
        for column in "font_code2000", "font_arial_unicode_ms":
            return _filter_mappings_by_value(mappings, column, value, country)


if __name__ == "__main__":
    # derive_currency_code("Z$", is_primary_currency=False)
    # derive_currency_code(
    #     "$", country="United States"
    # )  # only US in the list so will pass without country param but if is_primary_currency = False, this would fail
    # derive_currency_code(
    #     "£"
    # )  # pass since only GBP for £ but will fail if is_primary_currency = False
    print(derive_currency_code("&#8364;"))  # pass
