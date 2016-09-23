// For dealing with macros
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