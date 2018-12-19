require([
  'jquery',
  'pat-base'
], function ($, Base) {
  'use strict';
  var Doclink = Base.extend({
    name: 'plominodoclink',
    parser: 'mockup',
    trigger: '.plomino-doclink',
    defaults: {},
    init: function () {
      var self = this;
      var input  = self.$el.find('input[type="hidden"]');
      var single_select = self.$el.find('.single-select-widget');
      var $single_select = $(single_select[1]);
      var multi_select = self.$el.find('.multi-select-widget');
      var $multi_select = $(multi_select[1]);
      var $input = $(input[0]);

      if (multi_select.length) {
        var multi_select_value = JSON.parse(multi_select[1].dataset['list']);
        $multi_select.select2('data',multi_select_value);
        $multi_select.change(function (evt) {
        // select2 support tagging, which is not what we expect for doclink, so remove all tagging values
        if (evt.added) {
          var option = evt.added;
          var selectedLabels = evt.val;
          if (option.id != option.text) {
            var docIds = JSON.parse($input.val());
            if (!docIds.includes(option.id)) {
              docIds.push(option.id);
              multi_select_value.push(option);
              $input.val(JSON.stringify((docIds)));
            } else {
              selectedLabels.pop();
              $multi_select.select2('data', multi_select_value);
            }
          } else {
              selectedLabels.pop();
              $multi_select.select2('data', multi_select_value);
          }
        }
        if (evt.removed) {
          var option = evt.removed;
          multi_select_value = multi_select_value.filter(function(item, index, arr){
            return item.id != option.id;
          });
          $multi_select.select2('data',multi_select_value);
          var docIds = JSON.parse($input.val());
          var filteredIds = docIds.filter(function(value, index, arr){
            return value != option.id;
          });
          $input.val(JSON.stringify((filteredIds)));
        }
      });
      }
      if ($single_select) {
        $single_select.change(function (evt) {
          // select2 support tagging, which is not what we expect for doclink, so remove all tagging values
          if (evt.added) {
            var option = evt.added;
            if (option.id != option.text) {
              $single_select.select2('data', option);
              $input.val(option.id);
            } else {
              $single_select.select2("val", "");
              $input.val("");
            }
          }
          if (evt.removed) {
            $input.val("");
          }
        });
      }

    }
  });
  return Doclink;
});
