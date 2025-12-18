import pandas as pd
import pytest
from common_utils.format_handler import currency as currency_mod


def test_derive_currency_code_from_unicode(monkeypatch):
    # craft a minimal mapping DataFrame expected by derive_currency_code
    df = pd.DataFrame(
        [
            {
                "unicode_decimal": "8364;",
                "unicode_hex": "20AC;",
                "font_code2000": "EURSYM",
                "font_arial_unicode_ms": "€",
                "currency_code": "EUR",
                "country": "European Union",
                "primary_currency": True,
                "country_and_currency": "European Union €",
            }
        ]
    )

    monkeypatch.setattr(currency_mod, "_GLOBAL_CURRENCY_MAPPING", df)

    # unicode lookup
    assert currency_mod.derive_currency_code("&#8364;") == "EUR"

    # unknown symbol should raise LookupError
    with pytest.raises(LookupError):
        currency_mod.derive_currency_code("$", is_primary_currency=True)
