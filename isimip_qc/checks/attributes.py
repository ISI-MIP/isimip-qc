import uuid
from email.utils import parseaddr
from datetime import datetime

from .. import __version__
from ..config import settings
from ..fixes import fix_set_global_attr, fix_remove_global_attr


def check_isimip_id(file):
    try:
        isimip_id = file.dataset.getncattr('isimip_id')
        file.info('Global attribute "isimip_id" found (%s).', isimip_id)
    except AttributeError:
        file.info('Global attribute "isimip_id" not yet set.', fix={
            'func': fix_set_global_attr,
            'args': (file, 'isimip_id', str(uuid.uuid4()))
        })


def check_isimip_qc_version(file):
    try:
        version = file.dataset.getncattr('isimip_qc_version')
        if version == __version__:
            file.info('Global attribute "isimip_qc_version" matches current tool version (%s).',
                      version)
        else:
            file.info('Global attribute "isimip_qc_version" (%s) does not match tool current tool version (%s).',
                      version, __version__, fix={
                          'func': fix_set_global_attr,
                          'args': (file, 'isimip_qc_version', __version__)
                      })
    except AttributeError:
        file.info('Global attribute "isimip_qc_version" not yet set.',
                  fix={
                      'func': fix_set_global_attr,
                      'args': (file, 'isimip_qc_version', __version__)
                  })


def check_isimip_protocol_version(file):
    protocol_version = settings.DEFINITIONS['commit']

    try:
        version = file.dataset.getncattr('isimip_protocol_version')
        if version == protocol_version:
            file.info('Global attribute "isimip_protocol_version" matches current protocol version (%s).',
                      version)
        else:
            file.info('Global attribute "isimip_protocol_version" (%s) does not match tool current protocol version (%s).',
                      version, protocol_version, fix={
                          'func': fix_set_global_attr,
                          'args': (file, 'isimip_protocol_version', protocol_version)
                      })
    except AttributeError:
        file.info('Global attribute "isimip_protocol_version" not yet set.',
                  fix={
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
            file.error('Global attribute "contact" does not contain a proper address (%s).', contact)
        else:
            file.info('Global attribute "contact" looks good.')
    except AttributeError:
        file.error('Global attribute "contact" is missing.')


def check_isimip_qc_date(file):
    datetime_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    try:
        date = file.dataset.getncattr('isimip_qc_pass_date')
        if date is not None:
            file.info('Global attribute "isimip_qc_pass_date" is set to "%s".',
                      date, fix={
                          'func': fix_set_global_attr,
                          'args': (file, 'isimip_qc_pass_date', datetime_now)
                      })
    except AttributeError:
        file.info('Global attribute "isimip_qc_pass_date" not yet set.',
                  fix={
                      'func': fix_set_global_attr,
                      'args': (file, 'isimip_qc_pass_date', datetime_now)
                  })


def check_history(file):
    try:
        file.dataset.getncattr('history')
        file.warn('Global attribute "history" is set and will get removed.',
                  fix={
                      'func': fix_remove_global_attr,
                      'args': (file, 'history')
                  })
    except AttributeError:
        pass
