import html
from bs4 import BeautifulSoup
import pandas as pd
from common_utils.io_handler.external import get_request
from common_utils.data_handler.array import chunk_iter
from common_utils.format_handler.typography import convert_camel_to_snake_case


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

    return fx_mapping


GLOBAL_CURRENCY_MAPPING = _get_global_currency_mapping()


def derive_currency_code(value, currency_code_type="font_code2000"):
    currency_code_types = GLOBAL_CURRENCY_MAPPING.columns.tolist()
    if currency_code_type not in currency_code_types:
        raise ValueError(
            f"currency_code_type must be one of {[code for code in currency_code_types if code != 'currency_code']}, got {currency_code_type}"
        )

    # unicode stuff
    if value.startswith("&#"):
        value = html.unescape(value)

    cur_code = GLOBAL_CURRENCY_MAPPING[
        GLOBAL_CURRENCY_MAPPING[currency_code_type] == value
    ].currency_code.values[0]

    if not cur_code:
        raise ValueError(f"Currency code not found for value: {value}")

    return cur_code


if __name__ == "__main__":
    _get_global_currency_mapping()
