import pytest

from ..utils.contact import match_addrs, match_contact


@pytest.mark.parametrize('contact,result', [
    (r"John Doe <john@example.com>", True),
    (r"John Doe <john@example.com>, Jane Smith <jane@company.org>", True),
    (r"John Doe (john@example.com)", True),
    (r"John Doe (john@example.com), Jane Smith (jane@company.org)", True),
    (r"John Doe <john+doe@example.com>", True),
    (r"John Doe <john@example.com>, Jane Smith <jane%smith@company.org>", True),
    # no TLD
    (r"John Doe <john@example>", False),
    (r"John Doe <john@example.com>, Jane Smith <jane@company>", False),
    # dot after @
    (r"John Doe <john@.com>", False),
    (r"John Doe <john@example.com>, Jane Smith <jane@.com>", False),
    # no @ → nothing to validate
    (r"no emails here at all", True),
    # double @@
    (r"John Doe <john@@example.com>", False),
    (r"John Doe <john@example.com>, Jane Smith <jane@@company.org>", False),
])
def test_match_addrs(contact, result):
    assert match_addrs(contact) == result


@pytest.mark.parametrize('contact,result', [
    (r"John Doe <john@example.com>", True),
    (r"John Doe <john@example.com>, Jane Smith <jane@company.org>", True),
    (r"John Doe <john@example.com>, Jane Smith <jane@company.org>, Alice <alice@domain.co.uk>", True),
    (r"John Doe <john@example.com>,Jane Smith <jane@company.org>", False),
    (r"invalid, John Doe <john@example.com>", False),
])
def test_match_contact(contact, result):
    assert match_contact(contact) == result
