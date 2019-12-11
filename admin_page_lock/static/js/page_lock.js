$(document).ready(function() {
    // Global values.
    var api_interval = parseInt($('#page_lock_api_interval').val());
    var csrf_token;
    var data_to_process;
    var locked_by_me;
    var user_reference;
    var messages;

    // End the script if `api_interval` is not defined.
    if (!api_interval) {
        return;
    }

    // Show page_lock_bar.
    $('#page_lock_bar').show();

    // Hide all buttons.
    $('#page_lock_refresh_button').hide();
    $('#page_lock_reload_button').hide();

    // Refresh page by clicking the button.
    $('#page_lock_refresh_button').on('click', function(){
        $(location).attr('href', get_full_url());
    });

    $('#page_lock_reload_button').on('click', function(){
        data_to_process = call_open_page_connection();
        update_page(data_to_process);
    });

    // Get full url of current page.
    var get_full_url = function() {
        return window.location.href;
    };

    // Get base url of current page.
    var get_base_url = function() {
        var full_url = get_full_url();
        var full_url_splitted = full_url.split('/');
        return full_url_splitted[0] + '//' + full_url_splitted[2];
    };

    var redirect_to_homepage = function() {
        var homepage = data_to_process.page_lock_settings.homepage;
        var homepage_url = get_base_url() + homepage;
        $(location).attr('href', homepage_url)
    };

    // Ajax function.
    var send_request = function(url, data, async=false) {
      var tmp = null;
      $.ajax({
        method: 'POST',
        url: url,
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: JSON.stringify(data),
        dataType: 'json',
        async: async,
        success: function(response) {
            tmp = response;
        }
      });

      return tmp;
    };

    // Get data from template.
    var get_template_data = function() {
        var template_data = JSON.parse($('#page_lock_template_data').val());
        messages = template_data.page_lock_settings.messages;
        return template_data;
    };

    var call_api = function(url) {
        var data = {
            'url': encodeURIComponent(get_full_url()),
            'user_reference': user_reference,
        };

        var response = null;
        var num = 0;
        do {
            response = send_request(url, data);
            num++;
            window.setTimeout(function(){}, 500);

        } while (!response && num <= 3);

        // When response is `null` then warn user by dialog and
        // redirect him to the homepage.
        if (!response) {
            alert(messages.message_problem);
            redirect_to_homepage();
        }

        return response;
    };

    var call_get_page_info_data = function() {
        var url = get_base_url() + '/page_lock/get_page_info/';

        return call_api(url);
    };

    var call_open_page_connection = function() {
        var url = get_base_url() + '/page_lock/open_page_connection/';

        return call_api(url);
    };

    var update_page = function(data) {
        $('#page_lock_message_display').text(messages.message_locked);

        // Show page_lock_menu.
        $('#page_lock_bar').show();

        // Update counter.
        $('#page_lock_counter_display').text(data.reconnect_in + ' ' + 'seconds');

        // Show `REFRESH BUTTON` when page is not locked.
        if (!data.is_locked) {
            $('#page_lock_refresh_button').show();
            $('#page_lock_message_display').text(messages.message_refresh);
        }

        // Show `RELOAD BUTTON` only for user that locks current page.
        if (data.is_locked && user_reference == data.locked_by) {
            $('#page_lock_reload_button').show();
            $('#page_lock_message_display').text(messages.message_reload);
        }

        // Hide `page_lock_block`
        if (data.is_locked && user_reference != data.locked_by) {
            $('.page_lock_block').hide();
        }

        // Redirect to homepage when `reconnect_in` is equal to zero.
        if (data.reconnect_in == 0 && locked_by_me) {
            redirect_to_homepage();
        }
    };

    var periodical_update = function() {
        if (!data_to_process) {
            // Initialize global values.
            data_to_process = get_template_data();
            csrf_token = data_to_process.page_lock_settings.csrf_token;
            user_reference = data_to_process.page_lock_settings.user_reference;
            locked_by_me = user_reference == data_to_process.locked_by;
        } else {
            // Get data from info API.
            data_to_process = call_get_page_info_data();
        }
        update_page(data_to_process);
    };

    // Call `periodical_update` once and then every `api_interval` [ms].
    template_data = get_template_data();

    periodical_update();
    window.process_data_interval = setInterval(periodical_update, api_interval);

    // Deactivate user leaving current page.
    $(window).on('beforeunload', function() {
        // When user click `REFRESH` button then page lock can not deactivate same user refreshing page.
        var url = get_base_url() + '/page_lock/close_page_connection/';
        var data = {
            'url': encodeURIComponent(get_full_url()),
            'user_reference': user_reference,
        };
        send_request(url, data, true);
        clearInterval(window.process_data_interval);
    });
});
