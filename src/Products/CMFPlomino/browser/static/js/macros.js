//TODO: extend so it can accept a list of associated forms
// - add becomes autocomplete
// - accept dict instead of list of values
// - columns is what to display
// - need to store formid for each row so can reedit

require([
    'jquery',
    'pat-base',
    'mockup-patterns-modal',
    'mockup-patterns-select2',
    'mockup-patterns-sortable',
    "pat-registry"
], function($, Base, Modal, Select2, sortable, registry) {
    'use strict';
    var DataGrid = Base.extend({
        name: 'plominomacros',
        parser: 'mockup',
        trigger: '.plomino-macros',
        defaults: {},
        init: function() {
            var self = this;
            self.rules = JSON.parse(self.$el.attr('data-rules'));
            self.form_urls = JSON.parse(self.$el.attr('data-form-urls'));

            var selectdata = []
            for (var group in self.form_urls) {
                selectdata.push( {
                    text:group,
                    children:self.form_urls[group].map(function(macro) {
                        if (macro.title != undefined) {
                            return {id:macro['url'], text:macro['title']};
                        }
                    })
                })
            }

            self.select2_args = {
                data:selectdata,
                separator:"\t", //important, needs to match with python code
                orderable:true,
                multiple:true,
                placeholder: 'add a new rule',
                formatSelection: self.formatMacro
            };

            var html = '';
            self.item = self.$el.find('li')[0].outerHTML;
            self.rules.map(function(rule) {
//                var new_item = $(item.html())
//                new_item.find('input').class('form_select pat-select2');
                html += self.item;
            });
            self.$el.prepend(html);
            self.rules.push([]);
            var i=0;
            self.$el.find('input').each(function(index, el) {
                var rule = self.rules[i];
                if (rule.map != undefined) {
                    rule = self.rules[i].map(function(macro) {
                        return {id:JSON.stringify(macro),text:''}
                    });
                } else {
                    // else rule is old style and not a list of macros yet
                    rule = {id:JSON.stringify(rule),text:''};
                }
                self.initInput.bind({widget:self})(el, rule);
                i++;
            });
            self.cleanup_inputs.bind({widget:self})();

        },
        initInput: function(el, rule) {
            var self = this.widget;
            var select = $(el).select2(self.select2_args);
            select.select2('data', rule);
            select.change(function(evt) {
                var macro_select = $(evt.target);
                if (evt.added != undefined) {
                    var url = evt.added.id;
                    var text = evt.added.text;

                    // first pop the value that just got added out until after the popup
                    var values = macro_select.select2('data')
                    values.pop();
                    macro_select.select2('data',values);

                    self.edit_macro.bind({widget:self})(macro_select, url, text, {}, values.length);
                } else if (evt.removed != undefined) {
                    var id = evt.removed.id;
                    self.cleanup_inputs.bind({widget:self})();
                }
                //evt.stopPropagation();
                //evt.preventDefault();
                return false;
            });
        },
        cleanup_inputs: function() {
            var self = this.widget;
            var count = self.$el.find('.select2-container').size();
            // remove any empty rules
            self.$el.find('.select2-container').each(function(index, el) {
                var select = $(el);
                var values = select.select2('data');
                if (values.length == 0 && index < count-1) {
                    $(el).closest('li').remove();
                }
                else {
                    // find the exisitng tags and make them editable
                    //TODO: should only do once
                    $(el).find('.plomino_edit_macro').each(function(i, el) {
                        $(el).on("click", function(evt) {
                            evt.preventDefault();
                            //TODO: how to get the value for this rendered one?
                            var value = values[i];
                            var macro = JSON.parse(value.id);
                            var edit_url = null;
                            var formid = macro['Form'];
                            // find the url for formid
                            for (var type_ in self.form_urls) {
                                self.form_urls[type_].map(function (url) {
                                    if (url.id == formid) {
                                        edit_url = url.url;

                                    }
                                });
                            }

                            self.edit_macro.bind({widget:self})(select, edit_url, macro.title, macro, i);
                        });
                    });
                }
                // if last one is not empty add a new one
                if (index == count-1 && values.length > 0) {
                    // add a new input at the bottom
                    var item = $(self.item).appendTo(self.$el);
                    item.find('input').each(function(index, el) {
                        self.initInput.bind({widget:self})($(el), []);
                    });
                }
            });
            new sortable(self.$el, {selector:'.plomino-macros-rule'});

        },
        formatMacro: function (macro) {
            if (macro.text) {
                return macro.text;
            }
            var macro = JSON.parse(macro.id);
            var formid = macro.Form;
            var type = 'do';
            if (formid.startsWith('macro_condition_')) {
                type = 'if';
            }
            return '<span class="plomino_edit_macro"><i>' + type + '</i>&nbsp;' +
                macro.title +
                '<i class="icon-pencil"></i></span>';
        },
        edit_macro: function(macro_select, url, text, data, index) {
            var self = this.widget;
            // decode the json, work out the form to call
            // do ajax POST request
            // popup modal
            // on success find and remove old json, replace it will new json

            jQuery.ajax({
                url: url,
                type: "POST",
                data: data
            }).done(function(html) {
                var edit_modal = new Modal(self.$el, {
                    html: html,
                    position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
                    actions: {
                        'input.plominoSave': {
                            onSuccess: function(modal, response, state, xhr, form) {
                                if(response.errors) {
                                    return false;
                                }
                                modal.hide();

                                // find the old value (if there) and replace it
                                var values = macro_select.select2('data');
                                // replace the item added with json
                                var formdata = {};
                                form.serializeArray().map(function(x){formdata[x.name] = x.value;});
                                if (formdata.title == undefined) {
                                    formdata['title'] = text;
                                }
                                values[index] = {id:JSON.stringify(formdata),text:''}
                                macro_select.select2('data',values);

                                self.cleanup_inputs.bind({widget:self})();

                                return false;

                            },
                            onError: function() {
                                // TODO: render errors in the form
                                window.alert(response.responseJSON.errors.join('\n'));
                                return false;
                            }
                        }
    //                    'input.plominoCancel': {
    //                        onClick: add_row.hide()
    //                    }
                    }
                }).show();
            });


//            self.$el.find('.edit-row').each(function(i, el) {
//                // first use AJAX to get the form so we can do a post
//                var url = $(el).attr('href').split('?',2);
//                $(el).on("click", function(evt) {
//                    evt.preventDefault();
//
//
//                });
//            });

        },
    });
    return DataGrid;
});