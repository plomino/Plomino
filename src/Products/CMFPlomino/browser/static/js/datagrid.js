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
                    edit_url += '&' + self.fields[k] + '=' + self.values[j][k];
                }
                html += '<tr><td class="actions"><a class="edit-row" href="' + edit_url + '"><i class="icon-pencil"></i></a>';
                html += '<a class="remove-row" href="#"><i class="icon-cancel"></i></a>';
                html += '<a class="up-row" href="#"><i class="icon-up-dir"></i></a>';
                html += '<a class="down-row" href="#"><i class="icon-down-dir"></i></a></td>';
                for(var i=0;i<self.col_number;i++) {
                    html += '<td>' + self.rows[j][i] + '</td>';
                }
                html += '</tr>';
            }
            html += '<tr><td class="actions"><a class="add-row" href="'+self.form_url+'"><i class="icon-plus"></i></a></td></tr>';
            table.html(html);
            var add_modal = new Modal(self.$el.find('.add-row'), {
                actions: {
                    'input.plominoSave': {
                        onSuccess: self.add.bind(self),
                        onError: function() {
                            // TODO: render errors in the form
                            window.alert(response.errors);
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
                            onError: function() {
                                // TODO: render errors in the form
                                window.alert(response.errors);
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
                self.input.val(JSON.stringify(self.values));
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