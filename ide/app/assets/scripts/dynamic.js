require(["jquery", "pat-base"], function($, Base) {
    "use strict";
    var Dynamic = Base.extend({
        name: "plominodynamic",
        parser: "mockup",
        trigger: "#plomino_form",
        defaults: {},
        init: function() {
            var self = this;
            self.refresh(this.$el);
            this.$el.find(":input").change(function(e) {
                self.refresh(e.target);
            });
            self.hidewhen_html = {};
            self.$el.find(".plomino-hidewhen").each(function(i, el) {
                self.hidewhen_html[$(el).attr("data-hidewhen")] = $(el).html();
            });
        },
        refresh: function(field) {
            var self = this;
            var data = self.getCurrentInputs();
            if (self.options.docid) {
                data._docid = self.options.docid;
            }
            data._hidewhens = self.getHidewhens();
            data._fields = self.getDynamicFields();
            data._validation = field.id;
            // Only evaluate if we have a hidewhen or dynamic field
            // important to serialize the object to string using param and
            // set traditional to true so no additional [] is appear in
            // Plone HTTPRequest variable
            // TODO(ivanteoh): Remove getCurrentInputs and use $("form").serialize() + '&' + $.param(extra_data_obj, true)
            if (data._hidewhens.length > 0 || data._fields.length > 0) {
                $.post(
                    self.options.url + "/dynamic_evaluation",
                    $.param(data, true),
                    function(response) {
                        self.applyHidewhens(response.hidewhens);
                        self.applyDynamicFields(response.fields);
                    },
                    "json"
                );
            }
        },
        getCurrentInputs: function() {
            var key, input, input_key, input_value, existing_value, new_list;
            var data = {};
            var inputs = $("form")
                .serialize()
                .split("&");
            for (key in inputs) {
                input = inputs[key].split("=");
                input_key = input[0];
                input_value = decodeURIComponent(input[1].replace(/\+/g, "%20"));
                // handle array
                if (input_key in data) {
                    existing_value = data[input_key];
                    new_list = [];
                    if (!Array.isArray(existing_value)) {
                        new_list.push(existing_value);
                        existing_value = new_list;
                    }
                    existing_value.push(input_value);
                    input_value = existing_value;
                }
                data[input_key] = input_value;
            }
            return data;
        },
        getHidewhens: function() {
            var self = this;
            var hidewhens = [];
            self.$el.find(".plomino-hidewhen").each(function(i, el) {
                hidewhens.push($(el).attr("data-hidewhen"));
            });
            return hidewhens;
        },
        getDynamicFields: function() {
            var self = this;
            var fields = [];
            self.$el.find(".dynamicfield").each(function(i, el) {
                fields.push($(el).attr("data-dynamicfield"));
            });
            return fields;
        },
        applyHidewhens: function(hidewhens) {
            var self = this;
            for (var i = 0; i < hidewhens.length; i++) {
                var hwid = hidewhens[i][0];
                var status = hidewhens[i][1];
                var resetOnHide = hidewhens[i][2];
                var area = self.$el.find('.plomino-hidewhen[data-hidewhen="' + hwid + '"]');
                if (status) {
                    area.hide();
                    if (resetOnHide) {
                        area.html(self.hidewhen_html[hwid]);
                        //need to reinit this html
                        area.find(":input").change(function(e) {
                            self.refresh(e.target);
                        });
                    }
                } else {
                    area.show();
                }
            }
        },
        applyDynamicFields: function(fields) {
            var self = this;
            for (var i = 0; i < fields.length; i++) {
                var fieldid = fields[i][0];
                var value = fields[i][1];
                var field = self.$el.find('.dynamicfield[data-dynamicfield="' + fieldid + '"]');
                field.text(value);
            }
        },
    });
    return Dynamic;
});
