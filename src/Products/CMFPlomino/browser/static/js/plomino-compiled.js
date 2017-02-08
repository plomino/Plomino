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
                ed.css('width', width);
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
                field.html(value);
            }
        }
    });
    return Dynamic;
});
define("plominodynamic", function(){});

require([
    'jquery',
    'pat-base',
    'mockup-patterns-modal'
], function($, Base, Modal) {
    'use strict';
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
            self.form_url = self.$el.attr('data-form-url');
            self.render();
        },
        setValue(value) {
            var self = this;
            self.input.val(value);
            self.input.change();
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
                for(var k=0;k<self.col_number;k++) {
                    var value = self.values[j][k] || '';
                    value = value.datetime ? value.datetime : value;
                    edit_url += '&' + self.fields[k] + '=' + value;
                }
                html += '<tr><td class="actions"><a class="edit-row" href="' + edit_url + '"><i class="icon-pencil"></i></a>';
                html += '<a class="remove-row" href="#"><i class="icon-cancel"></i></a>';
                html += '<a class="up-row" href="#"><i class="icon-up-dir"></i></a>';
                html += '<a class="down-row" href="#"><i class="icon-down-dir"></i></a></td>';
                for(var i=0;i<self.col_number;i++) {
                    var v = self.rows[j][i] ? self.rows[j][i] : '';
                    html += '<td>' + v + '</td>';
                }
                html += '</tr>';
            }
            html += '<tr><td class="actions"><a class="add-row" href="'+self.form_url+'"><i class="icon-plus"></i></a></td></tr>';
            table.html(html);
            var add_modal = new Modal(self.$el.find('.add-row'), {
                actions: {
                    'input.plominoSave': {
                        onSuccess: self.add.bind(self),
                        onError: function(response) {
                            window.alert(response.responseJSON.errors.join('\n'));
                            return false;
                        }
                    }
                }
            });
            self.$el.find('.edit-row').each(function(i, el) {
                var edit_modal = new Modal($(el), {
                    actions: {
                        'input.plominoSave': {
                            onSuccess: self.edit.bind({grid: self, row: i}),
                            onError: function(response) {
                                window.alert(response.responseJSON.errors.join('\n'));
                                return false;
                            }
                        }
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
            var self = this;
            if(!response.errors) {
                modal.hide();
                var raw = [];
                var rendered = [];
                for(var i=0;i<self.col_number;i++) {
                    raw.push(response[self.fields[i]].raw);
                    rendered.push(response[self.fields[i]].rendered);
                }
                self.values.push(raw);
                self.setValue(JSON.stringify(self.values));
                self.rows.push(rendered);
                self.render();
            }
            return false;
        },
        edit: function(modal, response, state, xhr, form) {
            var self = this.grid;
            var row_index = this.row;
            if(!response.errors) {
                modal.hide();
                var raw = [];
                var rendered = [];
                for(var i=0;i<self.col_number;i++) {
                    raw.push(response[self.fields[i]].raw);
                    rendered.push(response[self.fields[i]].rendered);
                }
                self.values[row_index] = raw;
                self.setValue(JSON.stringify(self.values));
                self.rows[row_index] = rendered;
                self.render();
            }
            return false;
        },
        remove: function(self, index) {
            self.values.splice(index, 1);
            self.setValue(JSON.stringify(self.values));
            self.rows.splice(index, 1);
            self.render();
            return false;
        },
        up: function(self, index) {
            if(index==0) return;
            self.values.splice(index-1, 0, self.values.splice(index, 1)[0]);
            self.setValue(JSON.stringify(self.values));
            self.rows.splice(index-1, 0, self.rows.splice(index, 1)[0]);
            self.render();
            return false;
        },
        down: function(self, index) {
            if(index==self.values.length-1) return;
            self.values.splice(index, 0, self.values.splice(index+1, 1)[0]);
            self.setValue(JSON.stringify(self.values));
            self.rows.splice(index, 0, self.rows.splice(index+1, 1)[0]);
            self.render();
            return false;
        }
    });
    return DataGrid;
});
define("plominodatagrid", function(){});
