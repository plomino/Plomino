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