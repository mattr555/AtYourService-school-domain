// Generated by CoffeeScript 1.6.3
(function() {
  jQuery(function() {
    var change_hours;
    change_hours = function(button, data) {
      var old_text;
      button.parents('tr').removeClass().addClass(data.data.row_class);
      button.parents('tr').children('.status-field').html(data.data.status);
      old_text = button.parents('tr').children('.hour-field').text();
      button.parents('tr').children('.hour-field').text(data.data.hours.toString() + old_text.slice(-4));
      return $('#total-hours').text(data.data.srv_hours + ' SRV, ' + data.data.led_hours + ' LED');
    };
    $('.btn-div').on('click', '.approve-button.btn-danger', function(e) {
      var button, event_id, response, type, user_id;
      e.stopPropagation();
      button = $(this);
      user_id = $('#userid').text();
      event_id = button.data('event-id');
      type = button.data('type');
      return response = $.ajax('/ajax/main/toggle_event_approval.json', {
        data: {
          'user_id': user_id,
          'event_id': event_id,
          'type': type
        },
        success: function(data) {
          button.removeClass('btn-danger').addClass('btn-success').html('Approve');
          return change_hours(button, data);
        },
        timeout: 3000,
        type: "POST"
      });
    });
    return $('.btn-div').on('click', '.approve-button.btn-success', function(e) {
      var button, event_id, response, type, user_id;
      e.stopPropagation();
      button = $(this);
      user_id = $('#userid').text();
      event_id = button.data('event-id');
      type = button.data('type');
      return response = $.ajax('/ajax/main/toggle_event_approval.json', {
        data: {
          'user_id': user_id,
          'event_id': event_id,
          'type': type
        },
        success: function(data) {
          button.removeClass('btn-success').addClass('btn-danger').html('Disapprove');
          return change_hours(button, data);
        },
        timeout: 3000,
        type: "POST"
      });
    });
  });

}).call(this);
