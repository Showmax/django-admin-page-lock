from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# API interval.
API_INTERVAL_DEFAULT = 30000  # [ms]
API_INTERVAL_REFERENCE = 'PAGE_LOCK_API_INTERVAL'
API_INTERVAL = getattr(
    settings, API_INTERVAL_REFERENCE, API_INTERVAL_DEFAULT)

# User can open same page in more then one tabs.
CAN_OPEN_MORE_TABS_DEFAULT = False
CAN_OPEN_MORE_TABS_REFERENCE = 'PAGE_LOCK_CAN_OPEN_MORE_TABS'
CAN_OPEN_MORE_TABS = getattr(
    settings, CAN_OPEN_MORE_TABS_REFERENCE, CAN_OPEN_MORE_TABS_DEFAULT)

# CRFS token.
DISABLE_CRSF_TOKEN_DEFAULT = False
DISABLE_CRSF_TOKEN_REFERENCE = 'PAGE_LOCK_DISABLE_CRSF_TOKEN'
DISABLE_CRSF_TOKEN = getattr(
    settings, DISABLE_CRSF_TOKEN_REFERENCE, DISABLE_CRSF_TOKEN_DEFAULT)

# Disable locking.
DISABLE_DEFAULT = False
DISABLE_REFERENCE = 'PAGE_LOCK_DISABLE'
DISABLE = getattr(settings, DISABLE_REFERENCE, DISABLE_DEFAULT)

# Handler.
HANDLER_CLASS_DEFAULT = 'admin_page_lock.handlers.PageLockHandler'
HANDLER_CLASS_REFERENCE = 'PAGE_LOCK_HANDLER_CLASS'
HANDLER_CLASS = getattr(
    settings, HANDLER_CLASS_REFERENCE, HANDLER_CLASS_DEFAULT)

# Handler functions:
HANDLER_FUNCTION_CLOSE_PAGE_CONNECTION = 'close_page_connection'
HANDLER_FUNCTION_GET_PAGE_INFO = 'get_page_info'
HANDLER_FUNCTION_OPEN_PAGE_CONNECTION = 'open_page_connection'

# Home page redirect.
HOMEPAGE_DEFAULT = '/'
HOMEPAGE_REFERENCE = 'PAGE_LOCK_HOMEPAGE'
HOMEPAGE = getattr(settings, HOMEPAGE_REFERENCE, HOMEPAGE_DEFAULT)

# Keep DB locks (possible to see history).
KEEP_DB_LOCKS_DEFAULT = False
KEEP_DB_LOCKS_REFERENCE = 'PAGE_LOCK_KEEP_DB_LOCKS'
KEEP_DB_LOCKS = getattr(settings, KEEP_DB_LOCKS_REFERENCE, KEEP_DB_LOCKS_DEFAULT)  # noqa: E501

# Messages (see documentation).
MESSAGES_DEFAUL = {
    'message_locked': _('Page is locked.'),
    'message_reload': _('You are the one who can edit. Click "RELOAD" button to stay on the page.'),  # noqa: E501
    'message_refresh': _('Click "REFRESH" button to start editting.'),
    'message_problem': _('Something happened, you will be redirected to homepage.'),  # noqa: E501
}
MESSAGES_REFERENCE = 'PAGE_LOCK_MESSAGES'
MESSAGES = getattr(settings, MESSAGES_REFERENCE, MESSAGES_DEFAUL)

# Times (see documentation).
TIMEOUT_DEFAULT = 6000  # [s]
TIMEOUT_REFERENCE = 'PAGE_LOCK_TIMEOUT'
TIMEOUT = getattr(settings, TIMEOUT_REFERENCE, TIMEOUT_DEFAULT)

# Model.
MODEL_DEFAULT = 'admin_page_lock.models.database_model.DatabasePageLockModel'
MODEL_REFERENCE = 'PAGE_LOCK_MODEL'
MODEL = getattr(settings, MODEL_REFERENCE, MODEL_DEFAULT)

# Redis.
REDIS_PREFIX = 'lock-page'
REDIS_SETTINGS_DEFAULT = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': '',
    'timeout': 5
}
REDIS_SETTINGS_REFERENCE = 'PAGE_LOCK_REDIS_SETTINGS'
REDIS_SETTINGS = getattr(
    settings, REDIS_SETTINGS_REFERENCE, REDIS_SETTINGS_DEFAULT)

# Url.
URL_IGNORE_PARAMETERS_DEFAULT = True
URL_IGNORE_PARAMETERS_REFERENCE = 'PAGE_LOCK_URL_IGNORE_PARAMETERS'
URL_IGNORE_PARAMETERS = getattr(
    settings, URL_IGNORE_PARAMETERS_REFERENCE, URL_IGNORE_PARAMETERS_DEFAULT)
