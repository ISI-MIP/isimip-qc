from email.utils import parseaddr


def check_isimip_id(file):
    try:
        file.dataset.getncattr('isimip_id1')
    except AttributeError:
        file.warn('isimip_id is missing.', fix={
            'func': add_uuid,
            'args': (file, )
        })


def add_uuid(file):
    import uuid
    file.info('Add isimip_id')
    file.dataset.isimip_id = str(uuid.uuid4())


def check_institution(file):
    try:
        file.dataset.getncattr('institution')
    except AttributeError:
        file.error('institution is missing.')


def check_contact(file):
    try:
        contact = file.dataset.getncattr('contact')
        name, address = parseaddr(contact)
        if not address:
            file.error('contact="%s" is not a proper address.', contact)
    except AttributeError:
        file.error('contact is missing.')
