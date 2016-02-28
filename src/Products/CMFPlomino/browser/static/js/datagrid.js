require([
    'jquery',
    'mockup-patterns-base',
    'mockup-patterns-modal'
], function($, Base, Modal) {
    'use strict';
    var DataGrid = Base.extend({
        name: 'plominodatagrid',
        trigger: '.plomino-datagrid',
        defaults: {},
        init: function() {
            var self = this;
            self.fields = self.$el.attr('data-fields').split(',');
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
                html += '<th>' + self.fields[i] + '</th>';
            }
            html += '</tr>';
            for(var j=0;j<self.rows.length;j++) {
                html += '<tr><td>Edit - <span class="remove-row">Remove</span> - <span class="up-row">Up</span> - <span class="down-row">Down</span></td>';
                for(var i=0;i<self.col_number;i++) {
                    html += '<td>' + self.rows[j][i] + '</td>';
                }
                html += '</tr>';
            }
            html += '<tr><td><a class="add-row" href="'+self.form_url+'">+</a></td></tr>';
            table.html(html);
            var modal = new Modal(self.$el.find('.add-row'), {
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
                var row = [];
                for(var i=0;i<self.col_number;i++) {
                    row.push(response[self.fields[i]]);
                }
                self.values.push(row);
                self.input.val(JSON.stringify(self.values));
                self.rows.push(row);
                self.render();
            }
            return false;
        },
        remove: function(self, index) {
            self.values.splice(index, 1);
            self.input.val(JSON.stringify(self.values));
            self.rows.splice(index, 1);
            self.render();
        },
        up: function(self, index) {
            if(index==0) return;
            self.values.splice(index-1, 0, self.values.splice(index, 1)[0]);
            self.input.val(JSON.stringify(self.values));
            self.rows.splice(index-1, 0, self.rows.splice(index, 1)[0]);
            self.render();
        },
        down: function(self, index) {
            if(index==self.values.length-1) return;
            self.values.splice(index, 0, self.values.splice(index+1, 1)[0]);
            self.input.val(JSON.stringify(self.values));
            self.rows.splice(index, 0, self.rows.splice(index+1, 1)[0]);
            self.render();
        }
    });
    return DataGrid;
});