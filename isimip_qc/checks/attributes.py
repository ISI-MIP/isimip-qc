from email.utils import parseaddr


def check_institution(file):
    institution = file.dataset.getncattr('institution')
    if institution is None:
        file.warn('institution is missing.')
        file.has_warnings = True


def check_contact(file):
    contact = file.dataset.getncattr('contact')
    if contact:
        name, address = parseaddr(contact)
        if not address:
            file.warn('contact="%s" is not a proper address.', contact)
            file.has_warnings = True
    else:
        file.warn('contact is missing.')
        file.has_warnings = True
