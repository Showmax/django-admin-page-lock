from __future__ import unicode_literals

from admin_page_lock.mixins.base_mixin import BaseLockingMixin
from admin_page_lock.settings import DISABLE


class PageLockViewMixin(BaseLockingMixin):
    def dispatch(self, req, *args, **kwargs):
        self.req = req
        return super(PageLockViewMixin, self).dispatch(req, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PageLockViewMixin, self).get_context_data(**kwargs)

        if not DISABLE:
            result = self._open_page_connection_data(self.req)
            context.update(self._add_extra_content(self.req, result))

        return context
