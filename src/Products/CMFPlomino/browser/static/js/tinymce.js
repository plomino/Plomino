(function() {
    tinymce.PluginManager.add('plomino', function(editor, url) {
        var isNotFormEditor = !$('body').hasClass('portaltype-plominoform');

        if (isNotFormEditor) {
            return ;
        }

        // Add a button that opens a window
        editor.addButton('plominofield', {
            image: '++resource++Products.CMFPlomino/img/PlominoField.png',
            onclick: function () { editFormElement(editor, url, 'field'); }
        });
        editor.addButton('plominoaction', {
            image: '++resource++Products.CMFPlomino/img/PlominoAction.png',
            onclick: function () { editFormElement(editor, url, 'action'); }
        });
        editor.addButton('plominosubform', {
            image: '++resource++Products.CMFPlomino/img/PlominoForm.png',
            onclick: function () { editFormElement(editor, url, 'subform'); }
        });
        editor.addButton('plominohidewhen', {
            image: '++resource++Products.CMFPlomino/img/PlominoHideWhen.png',
            onclick: function () { editFormElement(editor, url, 'hidewhen'); }
        });
        editor.addButton('plominocache', {
            image: '++resource++Products.CMFPlomino/img/PlominoCache.png',
            onclick: function () { editFormElement(editor, url, 'cache'); }
        });

    });

    var editFormElement = function(ed, url, elementType) {
        // If the form is being created, don't create the same command
        if (location.pathname.indexOf("++add++PlominoForm") != -1)
        {
            alert(ed.getLang('plomino_tinymce.edition_forbidden', 'Please save the form before using this button.'));
            return;
        }

        if (elementType === "field") {
            var elementClass = 'plominoFieldClass';
            var elementEditionPage = '@@tinymceplominoform/field_form';
            var elementIdName = 'fieldid';
        }
        else if (elementType === "action") {
            var elementClass = 'plominoActionClass';
            var elementEditionPage = '@@tinymceplominoform/action_form';
            var elementIdName = 'actionid';
        }
        else if (elementType === "subform") {
            var elementClass = 'plominoSubformClass';
            var elementEditionPage = '@@tinymceplominoform/subform_form';
            var elementIdName = 'subformid';
        }
        else if (elementType === "hidewhen") {
            var elementClass = 'plominoHidewhenClass';
            var elementEditionPage = '@@tinymceplominoform/hidewhen_form';
            var elementIdName = 'hidewhenid';
        }
        else if (elementType === "cache") {
            var elementClass = 'plominoCacheClass';
            var elementEditionPage = '@@tinymceplominoform/cache_form';
            var elementIdName = 'cacheid';
        }
        else
            return;

        // Find the element id
        // Select the parent node of the selection
        var selection = ed.selection.getNode();
        // If the node is a <span class="plominoFieldClass"/>, select all its content
        if (tinymce.DOM.hasClass(selection, elementClass))
        {
            ed.selection.select(selection);
            var elementId = selection.firstChild.nodeValue;

            // hide-when and cache zones start with start:id and finish with end:id
            if (elementType === "hidewhen" || elementType === "cache")
            {
                var splittedId = elementId.split(':');
                if (splittedId.length > 1)
                    elementId = splittedId[1];
            }
        }
        else if (elementType !== "hidewhen" && elementType !== "cache")
        {
            // If the selection contains a <span class="plominoFieldClass"/>, select all its content
            nodes = tinymce.DOM.select('span.' + elementClass, selection);
            if (nodes.length > 0)
            {
                // Search if a node in the found nodes belongs to the selection
                for (var i = 0; i < nodes.length; i++)
                {
                    if (ed.selection.getContent().indexOf(tinymce.DOM.getOuterHTML(nodes[i])) != -1)
                    {
                        var node = nodes[i];
                        break;
                    }
                }

                // If a node is found, select it
                if (node)
                {
                    ed.selection.select(node);
                    var elementId = node.firstChild.nodeValue;
                }
                // Else, keep the selection
                else
                    var elementId = ed.selection.getContent();
            }

            // Else, keep the selection
            else
                var elementId = ed.selection.getContent();
        }
        else
        {
            var elementId = '';
        }

        var base_url = $('body').attr('data-base-url');

        ed.windowManager.open({
            url : base_url + '/' + elementEditionPage + '?' + elementIdName + '=' + elementId,
            width : 600 + parseInt(ed.getLang('plomino_tinymce.delta_width', 0)),
            height : 400 + parseInt(ed.getLang('plomino_tinymce.delta_height', 0)),
            inline : 1
        }, {
            plugin_url : url,
        });
    };
})();