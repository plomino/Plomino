require([
    'jquery',
    'pat-base',
    'mockup-patterns-texteditor'
], function($, Base, TextEditor) {
    'use strict';
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