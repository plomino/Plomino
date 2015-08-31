require([
    'jquery',
    'mockup-patterns-base',
    'mockup-patterns-tree'
], function($, Base, Tree) {
    'use strict';
    var PlominoDesign = Base.extend({
        name: 'plominodesign',
        trigger: '.plomino-design',
        defaults: {},
        init: function() {
            var self = this;
            self.tree = new Tree(self.$el.find('.tree'), {
                dataUrl: self.options.treeUrl,
                onCreateLi: function(node, li) {
                    console.log(node);
                }
            });
            // $(".pat-tree").bind('tree.open', function(e) {console.log(e.node)});
        }
    });
    return PlominoDesign;
});