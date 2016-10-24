// Dynamically refresh Field edit forms
require([
    'jquery',
    'pat-base',
], function($, Base, Modal) {
    'use strict';
    var PlominoRefresh = Base.extend({
        name: 'plominorefresh',
        parser: 'mockup',
        trigger: 'body.template-edit.portaltype-plominofield',
        defaults: {},
        init: function() {
            var self = this;
            $('#form-widgets-field_type').change(function(e) {
                self.refresh(e)
            });
        },
        refresh: function(field) {
            var self = this;
            // Add a hidden input so we can handle the refresh
            var input = $("<input>")
               .attr("type", "hidden")
               .attr("name", "update.field.type").val("1");
            $('form#form').append($(input));
            $('form#form').submit();
        },
 });
    return PlominoRefresh;
});