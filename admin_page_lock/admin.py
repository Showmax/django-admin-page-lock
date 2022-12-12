from __future__ import unicode_literals

from django.contrib import admin

from admin_page_lock.models.database_model import DatabasePageLockModel


class DatabasePageLockModelAdmin(admin.ModelAdmin):
    fields = (
        "active",
        "user_reference",
        "locked",
        "url",
        "url_parameters",
        "tab_counter",
    )
    list_display = (
        "url",
        "url_parameters",
        "active",
        "user_reference",
        "locked",
        "formated_locked_at",
        "formated_locked_out",
        "tab_counter",
    )
    list_filter = (
        "active",
        "user_reference",
    )
    list_per_page = 20
    ordering = ("-locked_at",)

    def _get_formated_datetime(self, lock_datetime):
        return lock_datetime.strftime("%Y-%m-%d-%H-%M-%S")

    def formated_locked_at(self, obj):
        return self._get_formated_datetime(obj.locked_at)

    formated_locked_at.admin_order_field = "locked_at"
    formated_locked_at.allow_tags = True
    formated_locked_at.short_description = DatabasePageLockModel._meta.get_field(
        "locked_at"
    ).verbose_name  # noqa: E501

    def formated_locked_out(self, obj):
        return self._get_formated_datetime(obj.locked_out)

    formated_locked_out.admin_order_field = "locked_at"
    formated_locked_out.allow_tags = True
    formated_locked_out.short_description = DatabasePageLockModel._meta.get_field(
        "locked_out"
    ).verbose_name  # noqa: E501


admin.site.register(DatabasePageLockModel, DatabasePageLockModelAdmin)
