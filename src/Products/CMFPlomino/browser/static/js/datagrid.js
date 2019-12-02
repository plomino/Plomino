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
], function ($, Base, Modal, Select2) {
  'use strict';
  var DataGrid = Base.extend({
    name: 'plominodatagrid',
    parser: 'mockup',
    trigger: '.plomino-datagrid',
    defaults: {},
    init: function () {
      var self = this;
      self.fields = self.$el.attr('data-fields').split(',');
      self.columns = self.$el.attr('data-columns').split(',');
      self.input = self.$el.find('input[type="hidden"]');
      self.values = JSON.parse(self.input.val());
      self.rows = JSON.parse(self.$el.find('table').attr('data-rows'));
      self.col_number = self.fields.length;
      self.associated_form = self.$el.attr('data-associated-form');
      self.source_view = self.$el.attr('data-source-view');
      if (self.$el.attr('data-form-urls')) {
        self.form_urls = JSON.parse(self.$el.attr('data-form-urls'));
      } else {
        var urlRe = /(.*)\/(.*)\/OpenForm\?(.*)/;
        var formid = urlRe.exec(self.$el.attr('data-form-url'))[2];
        self.form_urls = [{'url': self.$el.attr('data-form-url'), "id": formid}];
      }

      var select2_template = self.$el.find('.select2-template > .pat-select2');
      var select = $(select2_template[1]);

      self.CustomModal = Modal.extend({
        render: function (options) {
          var self = this;
          self.emit('render');
          self.options.render.apply(self, [options]);
          self.emit('rendered');
          $(this.$modalDialog.find('.plominoClose')).attr('onclick', '$(".plone-modal-close")[0].click()');
        }
      });

      select.change(function (evt) {
        if (evt.added) {
          if (evt.added.id == "NEW_DOC") {
            var scope = function (window) {
              var add_modal = new self.CustomModal(select, {
                ajaxUrl: self.form_urls[0]['url'],
                ajaxType: "POST",
                position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
                actions: {
                  'input.plominoSave': {
                    onSuccess: self.add.bind(
                      {
                        grid: self,
                        formid: select.attr('data-formid')
                      }),
                    onError: function () {
                      // TODO: render errors in the form
                      window.alert(response.responseJSON.errors.join('\n'));
                      return false;
                    }
                  },
                }
              }).show();
            }(window.top);
          } else if (evt.added.object)
              self.add_from_selection(evt.added.object);
        }
        select.select2("val", "");
        return false;
      });
      self.render();
    },
    isFieldVisible: function (field) {
      var self = this;
      if (!self.source_view)
        return true;
      else {
        var colRe = /(('_view_'|'_form_')\/)?(.*)\/(.*)/;
        return field.match(colRe);
      }
    },
    setValue: function (value) {
      var self = this;
      self.input.val(value);
      self.input.change();
    },
    render: function () {
      var self = this;
      // save select2 before re-rerendering the table
      var select2_instance = self.$el.find('.select2-cell > .pat-select2');
      if (select2_instance.length) {
        select2_instance.detach();
        self.$el.find(".select2-template").append(select2_instance);
      }

      var table = self.$el.find('table');
      var html = '<tr><th></th>';
      for (var i = 0; i < self.col_number; i++) {
        var field = self.fields[i];
        if (self.isFieldVisible(field))
          html += '<th>' + self.columns[i] + '</th>';
      }
      html += '</tr>';
      for (var j = 0; j < self.rows.length; j++) {
        var edit_url = self.form_url;
        //var formid = self.values[j]['Form'];
        var formid = self.associated_form;
        for (var f = 0; f < self.form_urls.length; f++) {
          if (self.form_urls[f].id == formid) {
            edit_url = self.form_urls[f].url;
            break;
          }
        }
        edit_url += '&' + $.param(self.values[j]);
        //for(var k=0;k<self.values.length;k++) {
        //    edit_url += '&' + self.values.lenght[k] + '=' + self.values[j][k];
        //}
        html += '<tr><td class="actions"><a class="edit-row" href="' + edit_url + '" data-formid="' + formid + '"><i class="icon-pencil"></i></a>';
        html += '<a class="remove-row" href="#"><i class="icon-cancel"></i></a>';
        html += '<a class="up-row" href="#"><i class="icon-up-dir"></i></a>';
        html += '<a class="down-row" href="#"><i class="icon-down-dir"></i></a></td>';
        for (var i = 0; i < self.col_number; i++) {
          var field = self.fields[i];
          if (self.isFieldVisible(field)) {
            var v = self.rows[j][i] ? self.rows[j][i] : '';
            html += '<td>' + v + '</td>';
          }
        }
        html += '</tr>';
      }
      var form_select = "";
      var select2_template = self.$el.find('.select2-template > .pat-select2');
      if (self.form_urls.length > 1) {
        form_select = '<select class="form_select" data-pat="width:10em">'
        for (i = 0; i < self.form_urls.length; i++) {
          var form = self.form_urls[i];
          form_select += '<option value="' + form['url'] + '">' + form['title'] + '</option>'
        }
        form_select += '</select>'
      }
      if (self.form_urls[0] != undefined) {
        if (select2_template.length == 0)
          html += '<tr><td class="actions" colspan="5">' + form_select +
            '<a class="add-row" href="' + self.form_urls[0]['url'] +
            '" data-formid="' + self.form_urls[0]['id'] +
            '"><i class="icon-plus"></i></a></td></tr>';
        else {
          html += '<tr><td class="select2-cell" colspan="' + (self.col_number + 1) + '" ></td></tr>';

        }
      }
      table.html(html);

      if (select2_template.length > 0) {
        select2_template.detach();
        self.$el.find('.select2-cell').append(select2_template);
      }

      var add_row = self.$el.find('.add-row');
      self.$el.find('.form_select').each(function (index, el) {
        var formid;
        $(el).change(function () {
          var url = $(el).val()
          for (var f = 0; f < self.form_urls.length; f++) {
            if (self.form_urls[f].url == url) {
              formid = self.form_urls[f].id;
              break;
            }
          }
          add_row.attr('href', url).attr('data-formid', formid);
        });
      });
      add_row.click(function (evt) {
        evt.stopPropagation();
        evt.preventDefault();
        //HACK: modal is broken so we can't dynamically set the ajaxURL
        // bind to a dummy element instead.
        //var modal_bind = $(window.top.document).contents().find('body');
        var modal_bind = self.$el.find('.add-row i')
        var scope = function (window) {
          var add_modal = new self.CustomModal(modal_bind, {
            ajaxUrl: add_row.attr('href'),
            ajaxType: "POST",
            position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
            actions: {
              'input.plominoSave': {
                onSuccess: self.add.bind(
                  {
                    grid: self,
                    formid: add_row.attr('data-formid')
                  }),
                onError: function () {
                  // TODO: render errors in the form
                  window.alert(response.responseJSON.errors.join('\n'));
                  return false;
                }
              },
              //                    'input.plominoCancel': {
              //                        onClick: add_row.hide()
              //                    }
            }
          }).show();
        }(window.top);

      });

      self.$el.find('.edit-row').each(function (i, el) {
        // first use AJAX to get the form so we can do a post
        var url = $(el).attr('href').split('?', 2);
        $(el).on("click", function (evt) {
          evt.preventDefault();

          jQuery.ajax({
            url: url[0],
            type: "POST",
            data: url[1]
          }).done(function (html) {
            var edit_modal = new self.CustomModal(self.$el, {
              html: html,
              position: 'middle top', // import to be at the top so it doesn't reposition inside the iframe
              actions: {
                'input.plominoSave': {
                  onSuccess: self.edit.bind({
                    grid: self,
                    row: i,
                    formid: $(el).attr('data-formid')
                  }),
                  onError: function () {
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
      self.$el.find('.remove-row').each(function (index, el) {
        $(el).click(function () {
          self.remove(self, index);
        });
      });
      self.$el.find('.up-row').each(function (index, el) {
        $(el).click(function () {
          self.up(self, index);
        });
      });
      self.$el.find('.down-row').each(function (index, el) {
        $(el).click(function () {
          self.down(self, index);
        });
      });
    },
    CustomModal: function () {
      var self = this;
      return new Modal.extend({
        render: function (options) {
          var self = this;
          self.emit('render');
          self.options.render.apply(self, [options]);
          self.emit('rendered');
          $(this).find('.plominoClose').attr('onclick', '$(".plone-modal-close")[0].click()');
        }
      });
    },
    add: function (modal, response, state, xhr, form) {
      var self = this.grid;
      var formid = this.formid;
      if (!response.errors) {
        modal.hide();
        var raw = {};
        var rendered = [];
        var formdata = form.serializeArray();
        for (var i = 0; i < self.col_number; i++) {
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
        self.setValue(JSON.stringify(self.values));
        self.rows.push(rendered);
        self.render();
      }
      return false;
    },
    add_from_selection: function (doc) {
      var self = this;
      var raw = {};
      var rendered = [];
      for (var i = 0; i < self.col_number; i++) {
        if (self.fields[i] != undefined && self.fields[i] in doc) {
          rendered.push(doc[self.fields[i]]);
        } else {
          rendered.push('');
        }

      }
      for (var key in doc) {
        raw[key] = doc[key]
      }
      self.values.push(raw);
      self.setValue(JSON.stringify(self.values));
      self.rows.push(rendered);
      self.render();
    },
    edit: function (modal, response, state, xhr, form) {
      var self = this.grid;
      var row_index = this.row;
      var formid = this.formid;
      if (!response.errors) {
        modal.hide();
        var rendered = [];
        for (var i = 0; i < self.col_number; i++) {
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
        self.setValue(JSON.stringify(self.values));
        self.rows[row_index] = rendered;
        self.render();
      }
      return false;
    },
    remove: function (self, index) {
      self.values.splice(index, 1);
      self.setValue(JSON.stringify(self.values));
      self.rows.splice(index, 1);
      self.render();
      return false;
    },
    up: function (self, index) {
      if (index == 0) return;
      self.values.splice(index - 1, 0, self.values.splice(index, 1)[0]);
      self.setValue(JSON.stringify(self.values));
      self.rows.splice(index - 1, 0, self.rows.splice(index, 1)[0]);
      self.render();
      return false;
    },
    down: function (self, index) {
      if (index == self.values.length - 1) return;
      self.values.splice(index, 0, self.values.splice(index + 1, 1)[0]);
      self.setValue(JSON.stringify(self.values));
      self.rows.splice(index, 0, self.rows.splice(index + 1, 1)[0]);
      self.render();
      return false;
    }
  });
  return DataGrid;
});