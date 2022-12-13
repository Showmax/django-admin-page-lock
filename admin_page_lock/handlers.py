from __future__ import unicode_literals

import datetime
import logging

from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from admin_page_lock import settings
from admin_page_lock.settings import (
    API_INTERVAL,
    DISABLE_CRSF_TOKEN,
    HOMEPAGE,
    MAX_FAILED_CHECK,
    TIMEOUT,
)


class PageLockHandler(object):
    """
    Provides logic for all API using different models that have same
    API defined.
    """

    HANDLER_NAME = "Page-Lock-Handler"  # Used for logging messages.

    def __init__(self, req, model_class, *args, **kwargs):
        self.model_class = model_class
        self.page_settings = model_class.get_page_settings(req)

    def _get_now(self):
        return timezone.now()

    def _get_lock_settings(self):
        # TODO(vstefka) this settings can be specific for each page defined in
        # settings somehow or defined and stored in database. Right now, the
        # settings is same for all pages!
        lock_settings = {
            "csrf_token": get_token(self.page_settings["req"])
            if not DISABLE_CRSF_TOKEN
            else "",
            "homepage": HOMEPAGE,
            "messages": self.page_settings["messages"],
            "user_reference": self.page_settings["user_reference"],
        }

        return lock_settings

    def _log_message(self, message, status="debug"):
        # Log handler messages.
        loger_function = getattr(logging, status)
        page_url = self.page_settings["page_url"]
        user_reference = self.page_settings["user_reference"]

        loger_function(
            _('Handler: "{}"\nURL: "{}"\nUser: "{}"\nMessage: "{}"\n').format(
                self.HANDLER_NAME,
                page_url if page_url else "",
                user_reference if user_reference else "",
                message,
            )
        )

    def close_page_connection(self, req, *args, **kwargs):
        """
        Closes page connection. Remove data related to the current page
        from storage or set it up to non-active only if same user is locking
        current page.
        """
        self._log_message(_("Close page connection."))
        # Get data from storage.
        data = self.model_class.get_data(self.page_settings)

        # Deactivate lock if user is locking current page.
        if (
            data is not None
            and data["user_reference"] == self.page_settings["user_reference"]
            and data["tab_counter"] == 1
        ):
            self.model_class.deactivate(self.page_settings)
            return {"is_locked": False}
        elif (
            data is not None
            and data["user_reference"] == self.page_settings["user_reference"]
            and data["tab_counter"] >= 1
        ):
            # Deactivate previous data.
            self.model_class.deactivate(self.page_settings)
            self.model_class.set_data(
                self.page_settings,
                {
                    "locked_at": data["locked_at"],
                    "locked_out": data["locked_out"],
                    "user_reference": data["user_reference"],
                    "tab_counter": data["tab_counter"] - 1,
                },
            )
            return {"is_locked": True}

        return {"is_locked": False}

    def get_page_info(self, req, *args, **kwargs):
        """
        Returns page information:
         + is_locked            whether the page is locked (True/False);
         + locked_by            `user_reference` that locked the page;
         + page_lock_settings   returns general page lock settings;
         + reconnect_in         time interval when page might be available [s].
        """
        self._log_message(_("Get page info."))
        response_data = {"page_lock_settings": self._get_lock_settings()}
        # Get data from storage.
        data = self.model_class.get_data(self.page_settings)

        now = self._get_now()
        interval_threshold = (API_INTERVAL / 1000) * MAX_FAILED_CHECK  # (ms to s) * #

        # 0. Lost contact with page.
        if (
            data is not None
            and (now - data["last_checked"]).seconds >= interval_threshold
        ):
            self.model_class.deactivate(self.page_settings)
            data = self.model_class.get_data(self.page_settings)

        # 1. No user is locking the page.
        if data is None:
            is_locked = False
            locked_by = None
            reconnect_in = 0
            reconnected = False
        # 2. Page is locked by current user or by another user.
        else:
            is_locked = True
            locked_by = data["user_reference"]
            locked_out = data["locked_out"]
            now = self._get_now()
            dtime = locked_out - now

            reconnect_in = 0
            if dtime.seconds < TIMEOUT:
                reconnect_in = dtime.seconds

            # Note: parameter `reconnected` is not used right now.
            reconnected = False
            if self.page_settings["user_reference"] == data["user_reference"]:
                self.model_class.check_data(self.page_settings)
                reconnected = True

        response_data.update(
            {
                "is_locked": is_locked,
                "locked_by": locked_by,
                "reconnect_in": reconnect_in,
                "reconnected": reconnected,
            }
        )

        return response_data

    def open_page_connection(self, req, *args, **kwargs):
        """
        Opens/Reopens page connection and returns:
         + is_locked            whether page connection is locked (True/False);
         + locked_by            user locking current page;
         + page_lock_settings   current lock page configuratino;
         + reconnected          page is locked by same user;
         + reconnect_in         number of seconds when page might be available.
        """
        self._log_message(_("Open/Reopen page connection."))
        response_data = {"page_lock_settings": self._get_lock_settings()}
        # Get data from storage.
        data = self.model_class.get_data(self.page_settings)
        now = self._get_now()

        # 0. Lost contact with page.
        if (
            data is not None
            and (now - data["last_checked"]).seconds >= 2 * API_INTERVAL
        ):
            self.model_class.deactivate(self.page_settings)
            data = self.model_class.get_data(self.page_settings)

        # 1. Page is not locked and is going to be lock by current user.
        if data is None:
            is_locked = True
            locked_by = self.page_settings["user_reference"]
            reconnected = False
            reconnect_in = TIMEOUT

            locked_at = self._get_now()
            locked_out = locked_at + datetime.timedelta(seconds=TIMEOUT)

            self.model_class.set_data(
                self.page_settings,
                {
                    "locked_at": locked_at,
                    "locked_out": locked_out,
                    "user_reference": locked_by,
                    "tab_counter": 1,
                },
            )

        # 2. Page is locked by another user or user can't open multiple tabs.
        elif data is not None and (
            self.page_settings["user_reference"] != data["user_reference"]
            or not settings.CAN_OPEN_MORE_TABS
        ):
            is_locked = True
            locked_by = data["user_reference"]
            reconnected = False
            reconnect_in = TIMEOUT
            locked_out = data["locked_out"]
            now = self._get_now()
            dtime = locked_out - now
            if dtime.seconds < TIMEOUT:
                reconnect_in = dtime.seconds

        # 3. Page is locked by same user.
        elif (
            data is not None
            and self.page_settings["user_reference"] == data["user_reference"]
        ):
            is_locked = True
            locked_by = data["user_reference"]
            tab_counter = data["tab_counter"]
            reconnected = True
            reconnect_in = TIMEOUT

            # Deactivate previous data.
            self.model_class.deactivate(self.page_settings)

            # Store new data in storage.
            locked_at = self._get_now()
            locked_out = locked_at + datetime.timedelta(seconds=TIMEOUT)

            self.model_class.set_data(
                self.page_settings,
                {
                    "locked_at": locked_at,
                    "locked_out": locked_out,
                    "user_reference": locked_by,
                    "tab_counter": tab_counter + 1,
                },
            )

        # 4. Impossible situation, placed here for regression.
        else:
            raise RuntimeError("Can't open page connection due to erroneous state.")

        response_data.update(
            {
                "is_locked": is_locked,
                "locked_by": locked_by,
                "reconnected": reconnected,
                "reconnect_in": reconnect_in,
            }
        )

        return response_data
