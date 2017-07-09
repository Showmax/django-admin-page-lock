from __future__ import unicode_literals

import json

from django import forms
from django.http import HttpResponseRedirect
from admin_page_lock.mixins.base_mixin import BaseLockingMixin
from admin_page_lock.settings import DISABLE


class LockPageViewMixin(BaseLockingMixin):
    def dispatch(self, req, *args, **kwargs):
        self.req = req
        return super(LockPageViewMixin, self).dispatch(req, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LockPageViewMixin, self).get_context_data(**kwargs)

        if not DISABLE and self.lock_change_view:
            result = self._open_page_connection_data(self.req)
            context.update(self._add_extra_content(self.req, result))

        return context
