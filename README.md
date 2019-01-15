## Django Admin Page Lock

Page Lock for Django Admin allows developers to implement customizable locking of pages.
With Admin Page Locking, only the designated (typically first) user receives full rights.
Subsequent users only get rights assigned by the administrator. You can store page lock data in
your application's defined database.

Read more on [our blog](https://tech.showmax.com/2018/02/django-admin-page-lock/).

#### Use Case:
1. User-1 lands on a page. User1 has full rights (editing).
2. Users-N can view the page, but cannot use full rights (no editing).
3. User-1 leaves.
4. Whoever next enters, or refreshes, becomes User-1.

### Features
* two models for data storage (`redis` or `database`);
* developer can disable whole locking functionality;
* url of page being locked can be composed with or without url parameters;
* history of locks can be kept (time, username, ...);
* very customizable.

### Requirements
* Django 1.8, 1.9, 1.11, 2.0;
* Python 2.7, 3.6, 3.7.

### Instalation
* run `pip install django-admin-page-lock`;
* add `admin_page_lock` to `setings.py`;
* run `./manage.py migrate` or `./manage.py syncdb`.

### Configuration
* update template by adding:
    ```
    <div id="page_lock_bar">
        <div id="page_lock_message_display"></div>
        <div id="page_lock_counter_display"></div>
        <button type="button" id="page_lock_refresh_button">{% trans "REFRESH" %}</button>
        <button type="button" id="page_lock_reload_button">{% trans "RELOAD" %}</button>
        <input type="hidden" id="page_lock_template_data" value="{{ page_lock_template_data }}">
        <input type="hidden" id="page_lock_api_interval" value="{{ page_lock_api_interval }}">
    </div>
    ```
  or using template tags `page_lock_bar_bootstrap` or `page_lock_bar_plain`.
  Note:
  * to hide locking buttons for pages where locking logic is not needed, update template by adding js block:
  ```
  <script type="text/javascript">
    $(document).ready(function() {
        var api_interval = parseInt($('#page_lock_api_interval').val());
        if (!api_interval) {
            $('.page_lock_bar').hide();
        }
    });
  </script>
  ```;
* mark `html` items by `class=page_lock_block` to hide/show them;
* update `css` file in order to enhance included `html` code;
* views where you want to apply locking logic must be inherited from either `PageLockAdminMixin` or `PageLockViewMixin` for `django admin views` or `django views`, respectively;
* re-define parameters in your settings if you don't want to use default ones:

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

### APIs

Several `APIs` are listed below. These are implemented so that they can be used by both frontend (`js`)
and backend (`python`). The logic is implemented in `handlers.py` and depends on chosen model as well.

On the first glance, one could think that `GetPageInfo` and `OpenPageConnection` are the same, but
the functionality of the first one doesn't change anything while the second one does.

#### 1. ClosePageConnection

| Method    |Name                | Type      | Description                                       |
|---------- |------------------- | --------- | ------------------------------------------------- |
| POST      | url                | string    | url of the page                                   |
| POST      | user_reference     | string    | reference of user (`id` or `current section` )    |
| POST      | csrf_token         | string    | generated `csfr` protection token                 |
| GET       | is_locked          | boolean   | whether the page is locked                        |

#### 2. GetPageInfo

| Method    |Name                | Type      | Description                                       |
|---------- |------------------- | --------- | ------------------------------------------------- |
| POST      | url                | string    | url of the page                                   |
| POST      | user_reference     | string    | reference of user (`id` or `current section` )    |
| POST      | csrf_token         | string    | generated `csfr` protection token                 |
| GET       | is_locked          | boolean   | whether the page is locked                        |
| GET       | locked_by          | string    | user_reference of user locking current page       |
| GET       | page_lock_settings | dictionary| various parameters of settings                    |
| GET       | reconnected        | boolean   | whether user is reconnected (not implemented yet) |

#### 3. OpenPageConnection

| Method    |Name                | Type      | Description                                       |
|---------- |------------------- | --------- | ------------------------------------------------- |
| POST      | url                | string    | url of the page                                   |
| POST      | user_reference     | string    | reference of user (`id` or `current section` )    |
| POST      | csrf_token         | string    | generated `csfr` protection token                 |
| GET       | is_locked          | boolean   | whether the page is locked                        |
| GET       | locked_by          | string    | user_reference of user locking current page       |
| GET       | page_lock_settings | dictionary| various parameters of settings                    |
| GET       | reconnected        | boolean   | whether user is reconnected (not implemented yet) |


### TODO
There are still several functionalities missing. I would appreciate any contribution.
* writing unit tests;
* finish using `CAN_OPEN_MORE_TABS` settings parameter;
* migrating logic related to reopening from `OpenPageConnection` to new API `ReopenPageConnection`;

### To be implemented soon:
1. User A lands on a page. The page is locked for this user.
2. User B attempts to open the page.
3. User B gets redirected to landing page (homepage, create new, and so on).

### Uses
* At [Showmax](https://tech.showmax.com/), we use this package as part of our Content Management System.
