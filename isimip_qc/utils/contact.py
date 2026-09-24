import re

candidate_pattern = r'\S+@\S+'
addr_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
name_pattern = fr'[^<>,\s][^<>,]*\s<{addr_pattern}>'
full_pattern = fr'^{name_pattern}([,;]\s{name_pattern})*$'


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


def normalize_contact(contact):
    # "," is the canonical separator, ";" is merely tolerated (c088183);
    # rebuild the string from the individual contacts it matches, which
    # rewrites separator semicolons to commas but leaves a semicolon inside
    # a display name untouched. A leading ";" is a legal name character, so
    # ";"-separated names absorb the separator and need to be cleaned up.
    names = re.findall(name_pattern, contact)
    if len(names) > 1:
        names[1:] = [name.lstrip(';').lstrip() for name in names[1:]]
    return ', '.join(names)
