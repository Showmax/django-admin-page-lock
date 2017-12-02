from __future__ import unicode_literals

import json

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from admin_page_lock.settings import (
    MESSAGES,
    URL_IGNORE_PARAMETERS
)
from urlparse import (
    parse_qsl,
    urlparse,
    urlsplit,
)


class BasePageLockModel(object):
    @classmethod
    def _get_page_full_url(cls, req):
        if hasattr(req, 'body') and 'url' in req.body:
            # Get `url` from body (JS call).
            page_full_url = json.loads(req.body)['url']
        else:
            # Get `url` by request function (Django view/adminview).
            page_full_url = req.get_full_path()

        return page_full_url

    @classmethod
    def _get_page_url_parameters(cls, req):
        # Returns string containing query parameters of the `url` with `_`
        # instead of `=`.
        if URL_IGNORE_PARAMETERS:
            return ''

        page_full_url = cls._get_page_full_url(req)

        try:
            parse_result = urlparse(page_full_url)
        except KeyError:
            raise

        if parse_result.query:
            return '_'.join(
                '_'.join([i, j])
                for i, j in parse_qsl(parse_result.query)
            )

        return ''

    @classmethod
    def _get_page_url(cls, req):
        # Returns url without parameters.
        page_full_url = cls._get_page_full_url(req)

        try:
            parse_result = urlsplit(page_full_url)
        except KeyError:
            raise

        return parse_result.path

    @classmethod
    def _get_session_key(cls, req):
        if hasattr(req, 'session'):
            return req.session.session_key

        return None

    @classmethod
    def _get_user_reference(cls, req):
        # Get username.
        username = cls._get_username(req)
        if username is not None:
            return str(username)

        # Get section.
        session_key = cls._get_session_key(req)
        if session_key is not None:
            return str(session_key)

        # Get user_reference from post.
        # curl -X POST -H "Accept: application/json"
        # -d '{"user_reference": "vstefka", "url": "page1"}'
        # "http://127.0.0.1:8000/page_lock/get_page_info/"
        try:
            return json.loads(req.body)['user_reference']
        except (KeyError, ValueError):
            pass

        raise Exception(_('User reference is not defined.'))

    @classmethod
    def _get_username(cls, req):
        if hasattr(req, 'user'):
            return req.user.username

        return None

    def deactivate(cls, page_settings):
        raise ImproperlyConfigured(
            _('Function: "close_page_connection" is not implemented'))

    @classmethod
    def get_data(cls, req, page_settings):
        raise ImproperlyConfigured(
            _('Function: "_get_data" is not implemented'))

    @classmethod
    def get_page_settings(cls, req):
        return {
            'messages': {
                i: str(j)
                for i, j in MESSAGES.items()
            },
            'page_url_parameters': cls._get_page_url_parameters(req),
            'page_url': cls._get_page_url(req),
            'req': req,
            'user_reference': cls._get_user_reference(req)
        }

    @classmethod
    def set_data(cls, req, page_settings, data):
        raise ImproperlyConfigured(
            _('Function: "_set_data" is not implemented'))
