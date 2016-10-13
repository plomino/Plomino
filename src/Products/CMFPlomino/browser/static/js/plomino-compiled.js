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
                var add_modal = new Modal(self.$el.find('.add-row i'), {
                    ajaxUrl: add_row.attr('href'),
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

            })

            self.$el.find('.edit-row').each(function(i, el) {
                var edit_modal = new Modal($(el), {
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
], function($, Base, Modal) {
    'use strict';
    var PlominoMacros = Base.extend({
        name: 'plominomacros',
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
define("plominomacros", function(){});
