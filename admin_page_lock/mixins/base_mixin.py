from __future__ import unicode_literals

import json

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from admin_page_lock.settings import (
    API_INTERVAL,
    CAN_OPEN_MORE_TABS,
    HANDLER_FUNCTION_CLOSE_PAGE_CONNECTION,
    HANDLER_FUNCTION_GET_PAGE_INFO,
    HANDLER_FUNCTION_OPEN_PAGE_CONNECTION,
)
from admin_page_lock.utils import get_page_lock_classes


class BaseLockingMixin(object):
    lock_change_view = False
    lock_changelist_view = False

    def _add_extra_content(self, req, data):
        # Adding extra content.
        extra_context = {
            "page_lock_template_data": json.dumps(data),
            "page_lock_api_interval": int(API_INTERVAL),  # must be integer
        }

        if (
            data["is_locked"]
            and data["page_lock_settings"]["user_reference"] != data["locked_by"]
        ):
            # Adding message when page is locked.
            self._add_message(req, data)

        return extra_context

    def _add_message(self, req, data):
        # Adding message when page is locked.
        # TODO(vstefka) move message to settings.
        # TODO(vstefka) add setting attribute to hide the message.
        messages.warning(
            req, _('This page is locked by "{}".'.format(data["locked_by"]))
        )

    @classmethod
    def _get_api_data(cls, req, handler_function_name):
        # Input argument `handler_function_name` must be one of defined in
        # settings.
        meta_name = "{}_data".format(handler_function_name)
        if meta_name not in req.META:
            # Get and initialize handler.
            handler_class, model_class = get_page_lock_classes()
            lock_handler = handler_class(req, model_class)

            # Get and run handler function to get response data.
            handler_function = getattr(lock_handler, handler_function_name)
            req.META[meta_name] = handler_function(req)

        return req.META[meta_name]

    @classmethod
    def _get_page_info_data(cls, req):
        return cls._get_api_data(req, HANDLER_FUNCTION_GET_PAGE_INFO)

    @classmethod
    def _is_locked(cls, req):
        # Returns `True` if the current page is not locked by same user
        # otherwise returns `False`.
        result = cls._get_page_info_data(req)
        if (
            result["is_locked"]
            and result["page_lock_settings"]["user_reference"] != result["locked_by"]
        ):
            return True

        return False

    def _close_page_connection_data(self, req):
        return self._get_api_data(req, HANDLER_FUNCTION_CLOSE_PAGE_CONNECTION)

    def _open_page_connection_data(self, req):
        return self._get_api_data(req, HANDLER_FUNCTION_OPEN_PAGE_CONNECTION)

    def _redirect_to_homepage(self, data):
        # TODO(vstefka) this is not working!
        # If page is already locked by user then redirect him/her
        # to `homepage` defined in `settings`.
        if not CAN_OPEN_MORE_TABS and data["reconnected"]:
            return True

        return False
