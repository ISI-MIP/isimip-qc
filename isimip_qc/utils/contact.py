import re

candidate_pattern = r'\S+@\S+'
addr_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
name_pattern = fr'[^<>,\s][^<>,]*\s<{addr_pattern}>'
full_pattern = fr'^{name_pattern}(,\s{name_pattern})*$'


def match_addrs(contact):
    candidates = re.findall(candidate_pattern, contact)
    if not candidates:
        return False

    for candidate in candidates:
        if not re.search(addr_pattern, candidate):
            return False

    return True


def match_contact(contact):
    match = re.match(full_pattern, contact)
    return bool(match)
