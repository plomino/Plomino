require([
    'jquery',
    'pat-base'
], function($, Base) {
    'use strict';
    var ComboBox = Base.extend({
        name: 'plominoselection',
        parser: 'mockup',
        trigger: '.combo-selectionfield',
        defaults: {},
        init: function() {
            var self = this;
            // Saving other value to a variable to swtich back and forth between other values option and real options
            // Need to clear the textbox after unchecking the other value option since the form can be submitted after that
            self.$el.find(':radio, :checkbox').each(function(index, el) {
                  self.$el.find(':text').each(function(index, textInput) {
                    if (el.value=='@@OTHER_VALUE' && el.checked) {
                      $(textInput).show();
                    }
                    else {
                      $(textInput).hide();
                    }
                  });
            });
            self.$el.find(':radio').change(function(el) {
                  self.$el.find(':text').each(function(index, textInput) {
                    if (el.target.value=='@@OTHER_VALUE' && el.target.checked) {
                      $(textInput).show();
                    }
                    else {
                      $(textInput).hide();
                      $(textInput).val("");
                    }
                  });
            });
            self.$el.find(':checkbox').change(function(el) {
                  self.$el.find(':text').each(function(index, textInput) {
                    if (el.target.value=='@@OTHER_VALUE')
                      if (el.target.checked) {
                          $(textInput).show();
                        }
                      else {
                        $(textInput).hide();
                        $(textInput).val("");
                      }
                  });
            });
        }
    });
    return ComboBox;
});