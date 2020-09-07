import uuid
from email.utils import parseaddr

from .. import __version__
from ..config import settings
from ..fixes import fix_set_global_attr


def check_isimip_id(file):
    try:
        isimip_id = file.dataset.getncattr('isimip_id')
        file.info('Global attribute isimip_id="%s" found.', isimip_id)
    except AttributeError:
        file.warn('Global attribute "isimip_id" is missing.', fix={
            'func': fix_set_global_attr,
            'args': (file, 'isimip_id', str(uuid.uuid4()))
        })


def check_isimip_qc_version(file):
    try:
        version = file.dataset.getncattr('isimip_qc_version')
        if version == __version__:
            file.info('Global attribute isimip_qc_version="%s" found.', version)
        else:
            file.warn('Global attribute isimip_qc_version="%s" should be "%s".', version, __version__, fix={
                'func': fix_set_global_attr,
                'args': (file, 'isimip_qc_version', __version__)
            })
    except AttributeError:
        file.warn('Global attribute "isimip_qc_version" is missing.', fix={
            'func': fix_set_global_attr,
            'args': (file, 'isimip_qc_version', __version__)
        })


def check_isimip_protocol_version(file):
    protocol_version = settings.DEFINITIONS['commit']

    try:
        version = file.dataset.getncattr('isimip_protocol_version')
        if version == protocol_version:
            file.info('Global attribute isimip_protocol_version="%s" found.', version)
        else:
            file.warn('Global attribute isimip_protocol_version="%s" should be "%s".', version, protocol_version, fix={
                'func': fix_set_global_attr,
                'args': (file, 'isimip_protocol_version', protocol_version)
            })
    except AttributeError:
        file.warn('Global attribute "isimip_protocol_version" is missing.', fix={
            'func': fix_set_global_attr,
            'args': (file, 'isimip_protocol_version', protocol_version)
        })


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
