"""Define template tag to generate page lock bar."""

from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def page_lock_bar_bootstrap(context):
    """Return html of page lock bar bootstrap html."""
    return render_to_string(
        "admin_page_lock/page_lock_bar_bootstrap.html",
        {
            "page_lock_template_data": context.get("page_lock_template_data"),
            "page_lock_api_interval": context.get("page_lock_api_interval"),
        },
    )


@register.simple_tag(takes_context=True)
def page_lock_bar_plain(context):
    """Return html of page lock bar plain html."""
    return render_to_string(
        "admin_page_lock/page_lock_bar_plain.html",
        {
            "page_lock_template_data": context.get("page_lock_template_data"),
            "page_lock_api_interval": context.get("page_lock_api_interval"),
        },
    )
