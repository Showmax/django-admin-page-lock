from __future__ import unicode_literals

from django import forms
from django.http import HttpResponseRedirect

from admin_page_lock.mixins.base_mixin import BaseLockingMixin
from admin_page_lock.settings import DISABLE


class PageLockAdminMixin(BaseLockingMixin):
    def change_view(self, req, object_id, form_url="", extra_context=None):
        if not DISABLE and self.lock_change_view:
            result = self._open_page_connection_data(req)
            extra_context = {} if extra_context is None else extra_context
            extra_context.update(self._add_extra_content(req, result))

        response = super(PageLockAdminMixin, self).change_view(
            req, object_id, form_url, extra_context=extra_context
        )
        if isinstance(response, HttpResponseRedirect):
            # Unlock the page if redirected.
            # Important when there is a redirect after saving a form.
            self._close_page_connection_data(req)

        return response

    def changelist_view(self, req, extra_context=None):
        if not DISABLE and self.lock_changelist_view:
            result = self._open_page_connection_data(req)
            extra_context = {} if extra_context is None else extra_context
            extra_context.update(self._add_extra_content(req, result))

        response = super(PageLockAdminMixin, self).changelist_view(
            req, extra_context=extra_context
        )
        if isinstance(response, HttpResponseRedirect):
            # Unlock the page if redirected.
            # Important when there is a redirect after saving a form.
            self._close_page_connection_data(req)

        return response

    def get_actions(self, req):
        # TODO(vstefka) hide only actions that can change db.
        if not self._is_locked(req):
            return super(PageLockAdminMixin, self).get_actions(req)

        return None

    def get_form(self, req, obj=None, **kwargs):
        form = super(PageLockAdminMixin, self).get_form(req, obj, **kwargs)

        if self._is_locked(req):
            for field_name in [
                i
                for i, j in form.base_fields.items()
                if issubclass(type(j), forms.FileField)
            ]:
                form.base_fields[field_name].widget.attrs["disabled"] = "disabled"

        return form

    def get_prepopulated_fields(self, req, obj=None):
        # It is not possible to pre-populate fields with readonly fields.
        if self._is_locked(req):
            return {}

        return super(PageLockAdminMixin, self).get_prepopulated_fields(req, obj)

    def get_readonly_fields(self, req, obj=None):
        readonly_fields = super(PageLockAdminMixin, self).get_readonly_fields(req, obj)

        if self._is_locked(req):
            readonly_fields = list(readonly_fields) + list(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )

        return tuple(readonly_fields)

    def has_add_permission(self, req, *args):
        can_add = super(PageLockAdminMixin, self).has_add_permission(req, *args)

        if can_add and not self._is_locked(req):
            return True

        return False

    def has_delete_permission(self, req, obj=None):
        can_delete = super(PageLockAdminMixin, self).has_delete_permission(req, obj)

        if can_delete and not self._is_locked(req):
            return True

        return False

    @property
    def media(self):
        media = super(PageLockAdminMixin, self).media + forms.Media(
            js=("js/page_lock.js",),
        )

        return media
