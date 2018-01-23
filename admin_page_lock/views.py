from __future__ import unicode_literals

import json

from django.http import (
    HttpResponse,
)
from django.views.generic.base import View
from admin_page_lock.settings import (
    HANDLER_FUNCTION_CLOSE_PAGE_CONNECTION,
    HANDLER_FUNCTION_GET_PAGE_INFO,
    HANDLER_FUNCTION_OPEN_PAGE_CONNECTION
)
from admin_page_lock.utils import get_page_lock_classes


class BasePageView(View):
    HANDLER_FUNCTION = None

    def post(self, req, *args, **kwargs):
        # Get and initialize handler.
        # TODO(vstefka) type of handler can depend on current page as well.
        try:
            # Get and initialize handler.
            handler_class, model_class = get_page_lock_classes()
            handler = handler_class(req, model_class)

            # Get and run handler function to get response data.
            handler_function = getattr(handler, self.HANDLER_FUNCTION)
            response_data = handler_function(req, *args, **kwargs)
        except Exception as e:
            # Propagate error to django in order to be able to log it.
            raise e

        response = HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )

        return response


class ClosePageConnection(BasePageView):
    """
    Call it when user is leaving the page.

    REQUEST:
     + csrf_token       CSRF token if `DISABLE_CRSF_TOKEN == True`;
     + url              url of locked page (with parameters);
     + user_reference   user reference visiting locked page.
    """
    HANDLER_FUNCTION = HANDLER_FUNCTION_CLOSE_PAGE_CONNECTION


class GetPageInfo(BasePageView):
    """
    Call it when user comes to the page at the first time. API then returns
    `RESPONSE` parameters based on `REQUEST` parameters and current`settings`.

    REQUEST:
     + csrf_token           CSRF token if `DISABLE_CRSF_TOKEN == True`;
     + url                  url of locked page (with parameters);
     + user_reference       user reference visiting locked page.
    RESPONSE:
     + is_locked            whether the page is locked (True/False);
     + locked_by            `user_reference` that locked the page;
     + page_lock_settings   current page lock type of the page (behaviou);
     + reconnect_in         number of seconds when page might be available.
    """
    HANDLER_FUNCTION = HANDLER_FUNCTION_GET_PAGE_INFO


class OpenPageConnection(BasePageView):
    """
    Call it when user wants to open/reopen page connection.

    REQUEST:
     + csrf_token           CSRF token if `DISABLE_CRSF_TOKEN == True`;
     + url                  url of locked page (with parameters);
     + user_reference       user reference visiting locked page.
    RESPONSE:
     + page_lock_settings   current lock page configuratino;
     + is_locked            whether page is locked (True/False);
     + reconnected          page is locked by same user;
     + reconnect_in         number of seconds when page might be available;
    """
    HANDLER_FUNCTION = HANDLER_FUNCTION_OPEN_PAGE_CONNECTION


# TODO(vstefka) think about migratting logic related to reopening from
# `OpenPageConnection` to new API `ReopenPageConnection`.
