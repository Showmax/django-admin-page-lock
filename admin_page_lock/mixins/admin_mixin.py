from __future__ import unicode_literals

from django import forms
from admin_page_lock.mixins.base_mixin import BaseLockingMixin
from admin_page_lock.settings import DISABLE


class LockPageAdminMixin(BaseLockingMixin):
    def change_view(self, req, object_id, form_url='', extra_context=None):
        if not DISABLE and self.lock_change_view:
            result = self._open_page_connection_data(req)
            extra_context = {} if extra_context is None else extra_context
            extra_context.update(self._add_extra_content(req, result))

        return super(LockPageAdminMixin, self).change_view(
            req,
            object_id,
            form_url,
            extra_context=extra_context
        )

    def changelist_view(self, req, extra_context=None):
        if not DISABLE and self.lock_changelist_view:
            result = self._open_page_connection_data(req)
            extra_context = {} if extra_context is None else extra_context
            extra_context.update(self._add_extra_content(req, result))

        return super(LockPageAdminMixin, self).changelist_view(
            req,
            extra_context=extra_context
        )

    def get_actions(self, req):
        # TODO(vstefka) hide only actions that can change db.
        if not self._is_locked(req):
            return super(LockPageAdminMixin, self).get_actions(req)

        return None

    def get_form(self, req, obj=None, **kwargs):
        form = super(LockPageAdminMixin, self).get_form(req, obj, **kwargs)

        if self._is_locked(req):
            for field_name in [
                i
                for i, j in form.base_fields.items()
                if issubclass(type(j), forms.FileField)
            ]:
                form.base_fields[field_name].widget.attrs['disabled'] = 'disabled'  # noqa

        return form

    def get_prepopulated_fields(self, req, obj=None):
        # It is not possible to pre-populate fields with readonly fields.
        if self._is_locked(req):
            return {}

        return super(LockPageAdminMixin, self).get_prepopulated_fields(req, obj)

    def get_readonly_fields(self, req, obj=None):
        readonly_fields = super(LockPageAdminMixin, self).get_readonly_fields(req, obj)  # noqa

        if self._is_locked(req):
            readonly_fields = list(readonly_fields) + list(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            )

        return tuple(readonly_fields)

    def has_add_permission(self, req):
        can_add = super(LockPageAdminMixin, self).has_add_permission(req)

        if can_add and not self._is_locked(req):
            return True

        return False

    def has_delete_permission(self, req, obj=None):
        can_delete = super(LockPageAdminMixin, self).has_delete_permission(req, obj)  # noqa

        if can_delete and not self._is_locked(req):
            return True

        return False

    @property
    def media(self):
        media = super(LockPageAdminMixin, self).media + forms.Media(
            js=(
                'js/page_lock.js',
            ),
        )

        return media
