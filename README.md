## Django Admin Page Lock

Page Lock for Django Admin allows developers to implement customizable locking of pages.
With Admin Page Locking, only the designated (typically first) user receives their regular
permissions assigned, including edit permissions (if available for the user).
Subsequent users only get limited permissions compared to those assigned to the first user, making
sure that user will not be granted permission to edit that object while the lock is
active and owned by another user. You can store page lock data in your application's
defined database.

Read more on [our blog](https://tech.showmax.com/2018/02/django-admin-page-lock/).

## Use Case:
1. `FirstUser` lands on a page. `FirstUser` has now full rights (editing), and
   it's the owner of the lock.
2. `AnyOtherUser` can view the page, but cannot use full rights (no editing).
3. `FirstUser` leaves the page.
4. Whoever next enters, or refreshes, has now full rights (editing) and is the
   owner of the lock.

## Features
* Two models for data storage: `redis` or `database`.
* The developer can disable whole locking functionality.
* Url of a page being locked can be composed with or without url parameters.
* History of locks can be kept (i.e. time, username).
* Very customizable.

## Requirements
* Django 1.8, 1.9, 1.11, 2.0, 2.1, 2.2;
* Python 2.7, 3.6, 3.7, 3.8, 3.9.

## Installation
Each of the following steps needs to be configured for the package to be fully functional.

### Getting the code
The source code is currently hosted on GitHub at: https://github.com/Showmax/django-admin-page-lock

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/django-admin-page-lock/).

To install it using pip, just run the following:
```bash
pip install django-admin-page-lock
```


### Prerequisites
Make sure to add `'admin_page_lock'` to your `INSTALLED_APPS` setting:
```python
INSTALLED_APPS = [
    # ...
    'admin_page_lock',
]
```
Don't forget to run `./manage.py migrate` or `./manage.py syncdb` after this change.

## Usage

### Templates
To enable the Admin Page Lock you need to update the template where do you want to
have it working. The templates `base.html`, `change_form.html` and `change_list.html`
should cover most of the use cases.

On the chosen template, you have two options:
1. Add the code bellow to the template, which gives you more freedom to customize it.
```html
{% load static %}
<html>
   <head>
       <!-- Add the page_lock.js to the template  -->
      <script src="{% static 'js/page_lock.js' %}"></script>
   </head>
   <body>
       <!-- ...  -->
       <div id="page_lock_bar">
       <div id="page_lock_message_display"></div>
       <div id="page_lock_counter_display"></div>
       <button type="button" id="page_lock_refresh_button">{% trans "REFRESH" %}</button>
       <button type="button" id="page_lock_reload_button">{% trans "RELOAD" %}</button>
       <input type="hidden" id="page_lock_template_data" value="{{ page_lock_template_data }}">
       <input type="hidden" id="page_lock_api_interval" value="{{ page_lock_api_interval }}">
       <!-- ...  -->
   </body>
</html>
```
2. Use the template tags `page_lock_bar_bootstrap` or `page_lock_bar_plain`.
The javascript is added automatically when using this method.
```html
{% load page_lock_bar_bootstrap %}
...
{% page_lock_bar_bootstrap %}
```

#### Disabling the locking logic
To hide locking buttons for pages where locking logic is not needed,
update the needed templates by adding the javascript block below.
```html
<script type="text/javascript">
  $(document).ready(function() {
      var api_interval = parseInt($('#page_lock_api_interval').val());
      if (!api_interval) {
          $('.page_lock_bar').hide();
      }
  });
</script>
```

#### Hiding specific html items
Add the class `page_lock_block` to any html tag you want to hide from users that are not
currently holding the lock. One common usage for this feature is to hide submit
buttons for users that are not holding the lock, for example:
```html
<div class="page_lock_block">
   <input type="submit" value="Submit" />
</div>
```

### Views
Views where you want to apply the locking logic must be inherited, use:
* `PageLockAdminMixin` for Django Admin Views;
* `PageLockViewMixin` for Django Views.

```python
# example/models.py
from django.db import models
from admin_page_lock.mixins import PageLockViewMixin


class Example(PageLockViewMixin, models.Model):
    ...

# example/admin.py
from admin_page_lock.mixins import PageLockAdminMixin
from django.contrib import admin
from .models import Example


class ExampleAdmin(PageLockAdminMixin, admin.ModelAdmin):
    ...
```
  
### Settings parameters
Re-define parameters in your settings if you don't want to use default ones:

| Name                   | Type       | Description                                        |
| ---------------------- | ---------- | -------------------------------------------------- |
| API_INTERVAL           | integer    | interval between API calls from `js`               |
| CAN_OPEN_MORE_TABS     | boolean    | whether user can open one page in more tabs        |
| DISABLE_CRSF_TOKEN     | boolean    | whether app uses `CSRF` protection                 |
| DISABLE                | boolean    | switching off/on locking logic                     |
| HANDLER_CLASS          | string     | in case you want to define your handler            |
| HOMEPAGE               | string     | page to redirect user if something goes wrong      |
| KEEP_DB_LOCKS          | boolean    | keep locking history (only for DB model)           |
| MESSAGES               | dictionary | for customizing messages (not implemented yet)     |
| TIMEOUT                | integer    | interval user stays on the page without refreshing |
| MODEL                  | string     | where data is stored (`redis` or `database`)       |
| REDIS_SETTINGS         | dictionary | settings of app `redis`                            |
| URL_IGNORE_PARAMETERS  | boolean    | whether url parameters are taken into account      |

## APIs

Several `APIs` are listed below. These are implemented so that they can be used by both frontend (`js`)
and backend (`python`). The logic is implemented in `handlers.py` and depends on chosen model as well.

At a first glance, one could think that `GetPageInfo` and `OpenPageConnection` are the same, but
the functionality of the first one doesn't change anything while the second one does.

### 1. ClosePageConnection

| Method    |Name                | Type      | Description                                       |
|---------- |------------------- | --------- | ------------------------------------------------- |
| POST      | url                | string    | url of the page                                   |
| POST      | user_reference     | string    | reference of user (`id` or `current section` )    |
| POST      | csrf_token         | string    | generated `csfr` protection token                 |
| GET       | is_locked          | boolean   | whether the page is locked                        |

### 2. GetPageInfo

| Method    |Name                | Type      | Description                                       |
|---------- |------------------- | --------- | ------------------------------------------------- |
| POST      | url                | string    | url of the page                                   |
| POST      | user_reference     | string    | reference of user (`id` or `current section` )    |
| POST      | csrf_token         | string    | generated `csfr` protection token                 |
| GET       | is_locked          | boolean   | whether the page is locked                        |
| GET       | locked_by          | string    | user_reference of user locking current page       |
| GET       | page_lock_settings | dictionary| various parameters of settings                    |
| GET       | reconnected        | boolean   | whether user is reconnected (not implemented yet) |

### 3. OpenPageConnection

| Method    |Name                | Type      | Description                                       |
|---------- |------------------- | --------- | ------------------------------------------------- |
| POST      | url                | string    | url of the page                                   |
| POST      | user_reference     | string    | reference of user (`id` or `current section` )    |
| POST      | csrf_token         | string    | generated `csfr` protection token                 |
| GET       | is_locked          | boolean   | whether the page is locked                        |
| GET       | locked_by          | string    | user_reference of user locking current page       |
| GET       | page_lock_settings | dictionary| various parameters of settings                    |
| GET       | reconnected        | boolean   | whether user is reconnected (not implemented yet) |


## TODO
There are still several functionalities missing. I would appreciate any contribution.
* writing unit tests;
* finish using `CAN_OPEN_MORE_TABS` settings parameter;
* migrating logic related to reopening from `OpenPageConnection` to new API `ReopenPageConnection`;

## To be implemented soon:
1. User A lands on a page. The page is locked for this user.
2. User B attempts to open the page.
3. User B gets redirected to landing page (homepage, create new, and so on).

## Uses
* At [Showmax](https://tech.showmax.com/), we use this package as part of our Content Management System.
