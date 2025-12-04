from common_utils import emailer


def test_build_html_email_meesage_contains_body_and_style():
    style = "h1{color:red}"
    body = "<h1>Hi</h1>"
    html = emailer.build_html_email_meesage(style=style, body=body)
    assert style in html
    assert body in html
