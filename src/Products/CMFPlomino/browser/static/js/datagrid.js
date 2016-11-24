//TODO: extend so it can accept a list of associated forms
// - add becomes autocomplete
// - accept dict instead of list of values
// - columns is what to display
// - need to store formid for each row so can reedit

require([
    'jquery',
    'pat-base',
    'mockup-patterns-modal',
    'mockup-patterns-select2'
], function($, Base, Modal, Select2) {
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