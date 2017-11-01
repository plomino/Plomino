require([
    'jquery',
    'pat-base'
], function($, Base) {
    'use strict';
    var Attachmet = Base.extend({
        name: 'plominoattachment',
        parser: 'mockup',
        trigger: 'input[type="file"]',
        defaults: {},
        init: function() {
            this.$el.siblings('input[name="attachment-delete"][type="checkbox"]').css('display','none');
            this.$el.siblings('a.delete-attachment').on('click', function() {
              $(this).siblings('a.file-attachment[data-filename="'+$(this).data('filename')+'"]').css('display','none');
              $(this).siblings('input[name="attachment-delete"][data-filename="'+$(this).data('filename')+'"]').prop('checked', true);
              $(this).css('display','none');
            })
        }
    });
    return Attachmet;
});
