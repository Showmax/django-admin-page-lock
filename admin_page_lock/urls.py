from __future__ import unicode_literals

from django.conf.urls import url

from admin_page_lock.views import ClosePageConnection, GetPageInfo, OpenPageConnection

urlpatterns = [
    # Close Page Connection.
    url(
        r"^close_page_connection/$",
        ClosePageConnection.as_view(),
        name="page_lock_close_page_connection",
    ),
    # Get Page Info.
    url(
        r"^get_page_info/$", GetPageInfo.as_view(), name="page_lock_get_page_connection"
    ),
    # Open Page Connection.
    url(
        r"^open_page_connection/$",
        OpenPageConnection.as_view(),
        name="page_lock_open_page_connection",
    ),
]
