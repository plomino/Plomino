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
            self.input = self.$el.find('input[type="hidden"]');
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
                var rule = self.rules[i].map(function(macro) {
                    return {id:JSON.stringify(macro),text:''}
                });
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
                    self.add_macro.bind({widget:self})(macro_select, url, text);
                } else if (evt.removed != undefined) {
                    var id = evt.removed.id;
                }
                self.cleanup_inputs.bind({widget:self})();
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
                // if last one is not empty add a new one
                if (index == count-1 && values.length > 0) {
                    // add a new input at the bottom
                    var input = $(self.item).appendTo(self.$el);
                    self.initInput.bind({widget:self})(input, []);
                }
            });

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
            return '<span><i>' + type + '</i>&nbsp;' +
                macro.title +
                '<i class="icon-pencil"></i></span>';
        },
        add_macro: function(macro_select, url, text) {
            var self = this.widget;

            // first pop the value that just got added out until after the popup
            var values = macro_select.select2('data')
            values.pop();
            macro_select.select2('data',values);

            var modal_bind = self.$el.find('ul')
            var scope = function(window) {
                var add_modal = new Modal(modal_bind, {
                    ajaxUrl: url,
                    position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
                    actions: {
                        'input.plominoSave': {
                            onSuccess: function(modal, response, state, xhr, form) {
                                if(response.errors) {
                                    return false;
                                }
                                modal.hide();

                                // replace the item added with json
                                var formdata = {};
                                form.serializeArray().map(function(x){formdata[x.name] = x.value;});
                                if (formdata.title == undefined) {
                                    formdata['title'] = text;
                                }
                                values.push({id:JSON.stringify(formdata),text:''});
                                macro_select.select2('data',values);

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
            }(window.top);
        }
    });
    return DataGrid;
});