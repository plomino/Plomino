require([
    'jquery',
    'pat-base'
], function($, Base) {
    'use strict';
    var Dynamic = Base.extend({
        name: 'plominodynamic',
        parser: 'mockup',
        trigger: '#plomino_form',
        defaults: {},
        init: function() {
            var self = this;
            this.$el.find(':input').change(function(e) {
                self.refresh(e.target);
            });
        },
        refresh: function(field) {
            var self = this;
            var data = self.getCurrentInputs();
            if(self.options.docid) {
                data._docid = self.options.docid;
            }
            data._hidewhens = self.getHidewhens();
            data._fields = self.getDynamicFields();
            data._validation = field.id;
            $.post(self.options.url + '/dynamic_evaluation',
                data,
                function(response) {
                    self.applyHidewhens(response.hidewhens);
                    self.applyDynamicFields(response.fields);
                },
                'json');
        },
        getCurrentInputs: function() {
            var data = {};
            var inputs = $("form").serialize().split("&");
            for(var key in inputs) {
                data[inputs[key].split("=")[0]] = inputs[key].split("=")[1];
            }
            return data;
        },
        getHidewhens: function() {
            var self = this;
            var hidewhens = [];
            self.$el.find('.plomino-hidewhen').each(function(i, el) {
                hidewhens.push($(el).attr('data-hidewhen'));
            });
            return hidewhens;
        },
        getDynamicFields: function() {
            var self = this;
            var fields = [];
            self.$el.find('.dynamicfield').each(function(i, el) {
                fields.push($(el).attr('data-dynamicfield'));
            });
            return fields;

        },
        applyHidewhens: function(hidewhens) {
            var self = this;
            for(var i=0; i<hidewhens.length; i++) {
                var hwid = hidewhens[i][0];
                var status = hidewhens[i][1];
                var area = self.$el.find('.plomino-hidewhen[data-hidewhen="'+hwid+'"]');
                if(status) {
                    area.hide();
                } else {
                    area.show();
                }
            }
        },
        applyDynamicFields: function(fields) {
            var self = this;
            for(var i=0; i<fields.length; i++) {
                console.log(fields[i]);
                var fieldid = fields[i][0];
                var value = fields[i][1];
                var field = self.$el.find('.dynamicfield[data-dynamicfield="'+fieldid+'"]');
                field.html(value);
            }
        }
    });
    return Dynamic;
});