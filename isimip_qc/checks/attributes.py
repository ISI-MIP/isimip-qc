from email.utils import parseaddr


def check_isimip_id(file):
    try:
        file.dataset.getncattr('isimip_id')
        file.info('Global attribute "isimip_id" found')
    except AttributeError:
        file.warn('Global attribute "isimip_id" is missing.', fix={
            'func': fix_add_uuid,
            'args': (file, )
        })


def fix_add_uuid(file):
    import uuid
    file.info('Adding isimip_id')
    file.dataset.isimip_id = str(uuid.uuid4())


def check_institution(file):
    try:
        file.dataset.getncattr('institution')
    except AttributeError:
        file.error('Global attribute "institution" is missing.')


def check_contact(file):
    try:
        contact = file.dataset.getncattr('contact')
        name, address = parseaddr(contact)
        if not address:
            file.error('Global attribute "contact (%s)" is not a proper address.', contact)
        else:
            file.info('Global attribute "contact" looks good.')
    except AttributeError:
        file.error('Global attribute "contact" is missing.')
