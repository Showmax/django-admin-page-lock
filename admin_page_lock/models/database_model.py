from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from admin_page_lock.models.base_model import BasePageLockModel
from admin_page_lock.settings import (
    KEEP_DB_LOCKS,
    URL_IGNORE_PARAMETERS,
)


class DatabasePageLockModel(BasePageLockModel, models.Model):
    """
    Parameters:
      + active       whether data is still active
      + locked       whether page is locked
      + locked_at    time when page was locked
      + locked_out   time when page will be unlocked
      + locked_by    user_reference of user that locked page
      + parameters   url parameters in JSON
      + url          url of locked page
    """
    url = models.URLField()
    url_parameters = models.CharField(max_length=1024, null=True, blank=True)
    active = models.BooleanField(default=True)
    user_reference = models.CharField(max_length=255, null=True, blank=True)
    locked = models.BooleanField(default=True)
    locked_at = models.DateTimeField(db_index=True)
    locked_out = models.DateTimeField(db_index=True)

    def __unicode__(self):
        return '{}'.format(self.pk)

    @classmethod
    def _get_query_kwargs(cls, page_settings):
        query_kwargs = {
            'active': True,
            'url': page_settings['page_url'],
        }
        if not URL_IGNORE_PARAMETERS:
            query_kwargs['url_parameters'] = page_settings['page_url_parameters']  # noqa: E501

        return query_kwargs

    @classmethod
    def deactivate(cls, page_settings):
        query_kwargs = cls._get_query_kwargs(page_settings)
        page_locks = cls.objects.filter(**query_kwargs)
        if KEEP_DB_LOCKS:
            page_locks.update(active=False)
        else:
            page_locks.delete()

    @classmethod
    def get_data(cls, page_settings):
        query_kwargs = cls._get_query_kwargs(page_settings)
        page_locks = cls.objects.filter(**query_kwargs)

        # Filter out data with `locked_out` older then now.
        page_locks = page_locks.filter(locked_out__gt=timezone.now())

        # Get the latest instance of `DatabasePageLockModel` and check
        # its existence.
        page_lock = page_locks.first()
        if (
            page_lock is None or
            not isinstance(page_lock, cls)
        ):
            return None

        return {
            'locked_at': page_lock.locked_at,
            'locked_out': page_lock.locked_out,
            'user_reference': page_lock.user_reference
        }

    def save(self, *args, **kwargs):
        # Deactive current instance with `locked_out` older then now.
        if self.locked_out < timezone.now():
            self.active = False

        super(DatabasePageLockModel, self).save(*args, **kwargs)

    @classmethod
    def set_data(cls, page_settings, data):
        data['url'] = page_settings['page_url']
        if not URL_IGNORE_PARAMETERS:
            data['url_parameters'] = page_settings['page_url_parameters']

        try:
            cls.objects.create(**data)
        except cls.DoesNotExist:
            raise

    class Meta:
        ordering = ('locked_at',)
        app_label = 'admin_page_lock'
        verbose_name = 'Page Lock'
        verbose_name_plural = 'Page Locks'
