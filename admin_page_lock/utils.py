from __future__ import unicode_literals

import importlib

from django.utils.crypto import get_random_string

from admin_page_lock.settings import HANDLER_CLASS, MODEL


def get_page_lock_class(class_path):
    module_name, class_name = class_path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name)
        page_lock_class = getattr(module, class_name)
    except (ImportError, AttributeError):
        raise

    return page_lock_class


def get_page_lock_classes():
    handler_class = get_page_lock_class(HANDLER_CLASS)
    model_class = get_page_lock_class(MODEL)

    return handler_class, model_class


def get_new_csrf_token(csfr_key_lenght):
    return get_random_string(csfr_key_lenght)
