require([
    'jquery',
    'pat-base',
    'mockup-patterns-texteditor'
], function($, Base, TextEditor) {
    
    var PlominoFormula = Base.extend({
        name: 'plominoformula',
        parser: 'mockup',
        trigger: '.plomino-formula',
        defaults: {},
        init: function() {
            var self = this;
            var width = self.$el.width();
            self.$el.hide();
            var ed = $('<pre></pre>');
            ed.appendTo(self.$el.parent());
            self.ace = new TextEditor(ed);
            self.ace.init();
            // wait until ace is ok
            setTimeout(function() {
                self.ace.editor.getSession().setMode('ace/mode/python');
                // the width variable return 100px most of the time.
                // yet to find out why
                ed.css('width', '100%');
                self.ace.editor.resize();
                self.ace.setText(self.$el.val());
                self.ace.editor.on('change', function(){
                    self.$el.val(self.ace.editor.getValue());
                });
            }, 200);
        }
    });
    return PlominoFormula;
});
define("plominoformula", function(){});

require([
    'jquery',
    'pat-base'
], function($, Base) {
    
    var Table = Base.extend({
        name: 'plominotable',
        parser: 'mockup',
        trigger: '.plomino-table',
        defaults: {},
        init: function() {
            var self = this;
            self.init_search();
            self.init_sorting();
            self.refresh({});
            self.params = {};
        },
        refresh: function() {
            var self = this;
            if(self.options.source) {
                self.$el.find('tr:not(.header-row)').remove();
                var counter = self.$el.find('tr.header-row.count')
                counter.find('td').text('Loading...');
                $.get(self.options.source, self.params, function(data) {
                    var html = '';
                    for(var i=0; i<data.rows.length; i++) {
                        var row = data.rows[i];
                        html += '<tr><td><a href="'
                            + self.options.source
                            + '/../../document/' + row[0]
                            + '">' + row[1]
                            + '</a></td>';
                        if(row.length > 2) {
                            for(var j=2; j<row.length; j++) {
                                html += '<td>' + row[j] + '</td>';
                            }
                        }
                        html += '</tr>';
                    }
                    if(data.rows.length > 1) {
                        counter.find('td').text(data.rows.length + ' documents');
                    } else {
                        counter.find('td').text(data.rows.length + ' document');
                    }
                    counter.before(html);
                });
            }
        },
        init_search: function() {
            var self = this;
            var search = $('<form id="plomino-search"><input type="text" placeholder="Search"/></form>');
            self.$el.before(search);
            search.on('submit', function() {return false;});
            var wait;
            var filtered = false;
            search.on('keyup', function() {
                var query = $('#plomino-search input').val();
                if(query.length < 3 && !filtered) {
                    return;
                } 
                if(wait) {
                    clearTimeout(wait);
                }
                wait = setTimeout(function() {
                    self.params.search = query;
                    self.refresh();
                    if(query) {
                        filtered = true;
                    } else {
                        filtered = false;
                    }
                    clearTimeout(wait);
                }, 1000);
            });
        },
        init_sorting: function() {
            var self = this;
            self.$el.find('th').on('click', function() {
                self.$el.find('th').removeClass('icon-down-dir icon-up-dir');
                var sort_on = $(this).attr('data-column');
                if(sort_on == self.params.sorton) {
                    self.params.reverse = (self.params.reverse==1) ? 0 : 1;
                } else {
                    self.params.sorton = sort_on;
                    self.params.reverse = 0;
                }
                if (self.params.reverse === 0) {
                    $(this).addClass('icon-down-dir');
                } else {
                    $(this).addClass('icon-up-dir');
                }
                self.refresh();
            });
        }
    });
    return Table;
});
define("plominotable", function(){});

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
            self.refresh(this.$el);
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
                field.text(value);
            }
        }
    });
    return Dynamic;
});
define("plominodynamic", function(){});

require([
    'jquery',
    'pat-base',
    'mockup-patterns-modal',
    'mockup-patterns-select2'
], function($, Base, Modal, Select2) {

    var DataGrid = Base.extend({
        name: 'plominodatagrid',
        parser: 'mockup',
        trigger: '.plomino-datagrid',
        defaults: {},
        init: function() {
            var self = this;
            self.fields = self.$el.attr('data-fields').split(',');
            self.columns = self.$el.attr('data-columns').split(',');
            self.input = self.$el.find('input[type="hidden"]');
            self.values = JSON.parse(self.input.val());
            self.rows = JSON.parse(self.$el.find('table').attr('data-rows'));
            self.col_number = self.fields.length;
            if (self.$el.attr('data-form-urls')) {
                self.form_urls = JSON.parse(self.$el.attr('data-form-urls'));
            } else {
                self.form_urls = [{'url':self.$el.attr('data-form-url')}];
            }

            self.render();
        },
        render: function() {
            var self = this;
            var table = self.$el.find('table');
            var html = '<tr><th></th>';
            for(var i=0;i<self.col_number;i++) {
                html += '<th>' + self.columns[i] + '</th>';
            }
            html += '</tr>';
            for(var j=0;j<self.rows.length;j++) {
                var edit_url = self.form_url;
                var formid = self.values[j]['Form'];
                for (var f=0; f<self.form_urls.length; f++) {
                    if (self.form_urls[f].id == formid) {
                        edit_url = self.form_urls[f].url;
                        break;
                    }
                }
                edit_url += '&'+ $.param(self.values[j]);
                //for(var k=0;k<self.values.length;k++) {
                //    edit_url += '&' + self.values.lenght[k] + '=' + self.values[j][k];
                //}
                html += '<tr><td class="actions"><a class="edit-row" href="' + edit_url + '" data-formid="'+formid+'"><i class="icon-pencil"></i></a>';
                html += '<a class="remove-row" href="#"><i class="icon-cancel"></i></a>';
                html += '<a class="up-row" href="#"><i class="icon-up-dir"></i></a>';
                html += '<a class="down-row" href="#"><i class="icon-down-dir"></i></a></td>';
                for(var i=0;i<self.col_number;i++) {
                    var v = self.rows[j][i] ? self.rows[j][i] : '';
                    html += '<td>' + v + '</td>';
                }
                html += '</tr>';
            }
            var form_select="";
            if (self.form_urls.length > 1) {
                form_select = '<select class="form_select" data-pat="width:10em">'
                for (i=0; i<self.form_urls.length; i++) {
                    var form = self.form_urls[i];
                    form_select += '<option value="'+form['url']+'">'+form['title']+'</option>'
                }
                form_select += '</select>'
            }
            if (self.form_urls[0] != undefined) {
                html += '<tr><td class="actions" colspan="5">'+form_select+
                    '<a class="add-row" href="'+self.form_urls[0]['url']+
                    '" data-formid="'+self.form_urls[0]['id']+
                    '"><i class="icon-plus"></i></a></td></tr>';
            }
            table.html(html);
            var add_row = self.$el.find('.add-row');
            self.$el.find('.form_select').each(function(index, el) {
                var formid;
                $(el).change(function() {
                    var url =  $(el).val()
                    for (var f=0; f<self.form_urls.length; f++) {
                        if (self.form_urls[f].url == url) {
                            formid = self.form_urls[f].id;
                            break;
                        }
                    }
                    add_row.attr('href', url).attr('data-formid', formid);
                });
            });
            add_row.click(function(evt){
                evt.stopPropagation();
                evt.preventDefault();
                //HACK: modal is broken so we can't dynamically set the ajaxURL
                // bind to a dummy element instead.
                //var modal_bind = $(window.top.document).contents().find('body');
                var modal_bind = self.$el.find('.add-row i')
                var scope = function(window) {
                var add_modal = new Modal(modal_bind, {
                    ajaxUrl: add_row.attr('href'),
                    ajaxType: "POST",
                    position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
                    actions: {
                        'input.plominoSave': {
                            onSuccess: self.add.bind(
                                {grid: self,
                                 formid:add_row.attr('data-formid')
                                }),
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
            })

            self.$el.find('.edit-row').each(function(i, el) {
                // first use AJAX to get the form so we can do a post
                var url = $(el).attr('href').split('?',2);
                $(el).on("click", function(evt) {
                    evt.preventDefault();

                    jQuery.ajax({
                        url: url[0],
                        type: "POST",
                        data: url[1]
                    }).done(function(html) {
                        var edit_modal = new Modal(self.$el, {
                            html: html,
                            position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
                            actions: {
                                'input.plominoSave': {
                                    onSuccess: self.edit.bind({grid: self,
                                        row: i,
                                        formid: $(el).attr('data-formid')}),
                                    onError: function() {
                                        // TODO: render errors in the form
                                        window.alert(response.responseJSON.errors.join('\n'));
                                        return false;
                                    }
                                }
        //                        'input.plominoCancel': {
        //                            onClick: add_row.hide()
        //                        }
                            }
                        }).show();
                    });

                });
            });
            self.$el.find('.remove-row').each(function(index, el) {
                $(el).click(function() {self.remove(self, index);});
            });
            self.$el.find('.up-row').each(function(index, el) {
                $(el).click(function() {self.up(self, index);});
            });
            self.$el.find('.down-row').each(function(index, el) {
                $(el).click(function() {self.down(self, index);});
            });
        },
        add: function(modal, response, state, xhr, form) {
            var self = this.grid;
            var formid = this.formid;
            if(!response.errors) {
                modal.hide();
                var raw = {};
                var rendered = [];
                var formdata = form.serializeArray();
                for(var i=0;i<self.col_number;i++) {
                    if (self.fields[i] != undefined && self.fields[i] in response) {
                        rendered.push(response[self.fields[i]].rendered);
                    } else {
                        rendered.push('');
                    }

                }
                for (var key in response) {
                    raw[key] = response[key].raw
                }
                raw['Form'] = formid;
                self.values.push(raw);
                self.input.val(JSON.stringify(self.values));
                self.rows.push(rendered);
                self.render();
            }
            return false;
        },
        edit: function(modal, response, state, xhr, form) {
            var self = this.grid;
            var row_index = this.row;
            var formid = this.formid;
            if(!response.errors) {
                modal.hide();
                var rendered = [];
                for(var i=0; i<self.col_number; i++) {
                    if (self.fields[i] != undefined && self.fields[i] in response) {
                        rendered.push(response[self.fields[i]].rendered);
                    } else {
                        rendered.push('');
                    }
                }
                self.values[row_index]['Form'] = formid;
                // keep any internal data (e.g. ids from server). Same as normal doc would
                for (var key in response) {
                    self.values[row_index][key] = response[key].raw;
                }
                self.input.val(JSON.stringify(self.values));
                self.rows[row_index] = rendered;
                self.render();
            }
            return false;
        },
        remove: function(self, index) {
            self.values.splice(index, 1);
            self.input.val(JSON.stringify(self.values));
            self.rows.splice(index, 1);
            self.render();
            return false;
        },
        up: function(self, index) {
            if(index==0) return;
            self.values.splice(index-1, 0, self.values.splice(index, 1)[0]);
            self.input.val(JSON.stringify(self.values));
            self.rows.splice(index-1, 0, self.rows.splice(index, 1)[0]);
            self.render();
            return false;
        },
        down: function(self, index) {
            if(index==self.values.length-1) return;
            self.values.splice(index, 0, self.values.splice(index+1, 1)[0]);
            self.input.val(JSON.stringify(self.values));
            self.rows.splice(index, 0, self.rows.splice(index+1, 1)[0]);
            self.render();
            return false;
        }
    });
    return DataGrid;
});
define("plominodatagrid", function(){});

require([
    'jquery',
    'pat-base'
], function($, Base) {
    'use strict';
    var Multipage = Base.extend({
        name: 'plominomultipage',
        parser: 'mockup',
        trigger: 'body.template-page.portaltype-plominoform #plomino_form input[name="plomino_current_page"]',
        defaults: {},
        init: function() {
            // Push the current page into the URL
            // The action is the current page
            var page = this.$el.parents('#plomino_form').attr('action');
            var stateObj = {multipage: 'multipage' };
            history.pushState(stateObj, '', page);
        }
    });
    return Multipage;
});
define("plominomultipage", function(){});

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
define("plominomacros", function(){});

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
define("plominomacropopup", function(){});

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
define("plominorefresh", function(){});
