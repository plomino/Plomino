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
    'mockup-patterns-backdrop',
    'mockup-utils',
    "pat-registry"
], function($, Base, Modal, Select2, Sortable, Backdrop, utils, registry) {
    'use strict';
    var MacroWidget = Base.extend({
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
                            return {id:macro.id, text:macro['title']};
                        }
                    })
                })
            }

            self.select2_args = {
                data:selectdata,
                separator:"\t", //important, needs to match with python code
                //orderable:true,
                multiple:true,
                allowNewItems: false,
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
            self.ids = {};
            self.rules.push([]);
            var i=0;
            self.$el.find('input').each(function(index, el) {
                var rule = self.rules[i];
                if (rule.map == undefined) {
                    //else rule is old style and not a list of macros yet
                    rule = [rule];
                }
                rule = rule.map(function(macro) {
                    if (macro['_macro_id_']) {
                        self.ids[macro['_macro_id_']]=true;
                    }
                    return {id:JSON.stringify(macro),text:''}
                });
                self.initInput.bind({widget:self})(el, rule);
                i++;
            });
            self.cleanup_inputs.bind({widget:self})();

            self.backdrop = new Backdrop(self.$el, {closeOnEsc:true, closeOnClick:false});
            self.loading = utils.Loading({backdrop:self.backdrop});


        },
        initInput: function(el, rule) {
            var self = this.widget;
            new Select2($(el), self.select2_args);
            // Select2 pattern orderable is broken. need to do it ourselves
            var select = $(el);
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

                            self.edit_macro.bind({widget:self})(select, formid, macro.title, macro, i);
                        });
                    });
                    new Sortable($(el).find(".select2-choices"), {
                        selector:'.select2-search-choice',
                        drop: function() {
                            $(el).select2('onSortEnd');
                        }});


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
            new Sortable(self.$el, {selector:'.plomino-macros-rule'});

        },
        formatMacro: function (macro) {
            if (macro.text) {
                return macro.text;
            }
            var macro = JSON.parse(macro.id);
            var formid = macro.Form;
            if (formid == 'or' || formid == 'and' || formid == 'nor') {
                return macro.title;
            }
            var type = 'do';
            if (formid.startsWith('macro_condition_')) {
                type = 'if';
            }
            return '<span class="plomino_edit_macro"><i>' + type + '</i>&nbsp;' +
                macro.title +
                '<i class="icon-pencil"></i></span>';
        },
        edit_macro: function(macro_select, formid, text, data, index) {
            var self = this.widget;

            // find the url for formid
            var edit_url = null;
            for (var type_ in self.form_urls) {
                self.form_urls[type_].map(function (url) {
                    if (url.id == formid) {
                        edit_url = url.url;

                    }
                });
            }

            //ensure we have an unique id since select2 doesn't allow two items the same
            var macroid = data['_macro_id_'];
            var i = 1;
            while (macroid==undefined || self.ids[macroid]) {
                macroid = formid + '_' + i;
                i++;
            }
            data['_macro_id_'] = macroid;
            self.ids[macroid] = true;

            //Special case. Urls that start with # have no popup
            if (edit_url.startsWith('#')) {
                var values = macro_select.select2('data');
                data['title'] = text;
                data['Form'] = formid;
                values.push({id:JSON.stringify(data),text:text});
                macro_select.select2('data',values);
                self.cleanup_inputs.bind({widget:self})();
                return
            }

            // decode the json, work out the form to call
            // do ajax POST request
            // popup modal
            // on success find and remove old json, replace it will new json

            self.backdrop.show();
            self.loading.show(true);

            jQuery.ajax({
                url: edit_url,
                type: "POST",
                data: data
            }).done(function(html) {
                self.loading.hide();
                self.backdrop.hide();
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
                                $.map(response, function(value, key) {formdata[key] = value.raw});
                                formdata['Form'] = formid;

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


        }
    });
    return MacroWidget;
});

// For the macro popup
require([
    'jquery',
    'pat-base',
    'mockup-patterns-modal',
], function($, Base, Modal) {
    'use strict';
    var PlominoMacros = Base.extend({
        name: 'plominomacropopup',
        parser: 'mockup',
        trigger: '.plomino-macro',
        defaults: {},
        init: function() {
            var self = this;
            // Remove any onclick values
            $('.plominoClose', self.$modal).each(function() {
                this.removeAttribute('onclick');
            });
            self.render();
        },
        render: function() {
            var self = this;
            // Close the modal when the close button is clicked
            $('.plominoClose', self.$modal)
              .off('click')
              .on('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                $(e.target).trigger('destroy.plone-modal.patterns');
            });
        }
 });
    return PlominoMacros;
});
