require([
    'jquery',
    'pat-base',
    'mockup-patterns-tree'
], function($, Base, Tree) {
    'use strict';
    var PlominoDesign = Base.extend({
        name: 'plominodesign',
        parser: 'mockup',
        trigger: '.plomino-design',
        defaults: {},
        init: function() {
            var self = this;
            self.tree = new Tree(self.$el.find('.tree'), {
                dataUrl: self.options.treeUrl,
                onCreateLi: function(node, li) {
                    var element = li.find('.jqtree-element');

                    // Database icon
                    if (node.type == 'database'){
                        element.prepend(
                          '<span class="icon-file-code"></span>'
                        );
                    }

                    // Form icon
                    if (node.type == 'form'){
                        element.prepend(
                          '<span class="icon-file-code"></span>'
                        );
                        element.append(
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/edit"><span class="icon-pencil" />Edit</a> </span>' +
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/view"><span class="icon-doc-text" />View</a> </span>' +
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/folder_contents"><span class="icon-folder-open" />Contents</a></span>'
                        );
                    }

                    // Field icons
                    if (node.type == 'fields'){
                        element.prepend(
                          '<span class="icon-field"></span>'
                        );
                    }
                    if (node.type == 'field'){
                        element.prepend(
                          '<span class="icon-field"></span>'
                        );
                        element.append(
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/edit"><span class="icon-pencil" />Edit</a> </span>' +
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/view"><span class="icon-doc-text" />View</a> </span>'
                        );
                    }

                    // Action icons
                    if (node.type == 'actions'){
                        element.prepend(
                          '<span class="icon-cog"></span>'
                        );
                    }
                    if (node.type == 'action'){
                        element.prepend(
                          '<span class="icon-cog"></span>'
                        );
                        element.append(
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/edit"><span class="icon-pencil" />Edit</a></span>'
                        );
                    }

                    // View icons
                    if (node.type == 'views'){
                        element.prepend(
                          '<span class="icon-doc-text"></span>'
                        );
                    }
                    if (node.type == 'view'){
                        element.prepend(
                          '<span class="icon-doc-text"></span>'
                        );
                        element.append(
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/edit"><span class="icon-pencil" />Edit</a></span>' +
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/view"><span class="icon-doc-text" />View</a></span>' +
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/folder_contents"><span class="icon-folder-open" />Contents</a></span>'
                        );
                    }
                    if (node.type == 'columns'){
                        element.prepend(
                          '<span class="icon-table"></span>'
                        );
                    }
                    if (node.type == 'column'){
                        element.prepend(
                          '<span class="icon-table"></span>'
                        );
                        element.append(
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/edit"><span class="icon-pencil" />Edit</a></span>'
                        );
                    }

                    // Agent icons
                    if (node.type == 'agents'){
                        element.prepend(
                          '<span class="icon-cog-alt"></span>'
                        );
                    }
                    if (node.type == 'agent'){
                        element.prepend(
                          '<span class="icon-cog-alt"></span>'
                        );
                        element.append(
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/edit"><span class="icon-pencil" />Edit</a></span>' +
                          '&nbsp;<span class="jqtree-common jqtree-title"><a href="' + node.url + '/runAgent"><span class="icon-link-ext" />Run</a></span>'
                        );
                    }
                }
            });

            // $(".pat-tree").bind('tree.open', function(e) {console.log(e.node)});
        }
    });
    return PlominoDesign;
});
