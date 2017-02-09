(function() {
    tinymce.PluginManager.add('plomino', function(editor, url) {

        // This plugin should only be active on a plomino form on the edit template
        var isFormEditor = $('body').hasClass('portaltype-plominoform') && $('body').hasClass('template-edit')

        if (!isFormEditor) {
            return;
        }

        // Add a button that opens a window
        editor.addButton('plominofield', {
            tooltip: 'Field',
            image: '++resource++Products.CMFPlomino/img/PlominoField.png',
            onclick: function () { editFormElement(editor, url, 'field'); }
        });
        editor.addButton('plominolabel', {
            tooltip: 'Label',
            image: '++resource++Products.CMFPlomino/img/PlominoLabel.png',
            onclick: function () { editFormElement(editor, url, 'label'); }
        });
        editor.addButton('plominoaction', {
            tooltip: 'Action',
            image: '++resource++Products.CMFPlomino/img/PlominoAction.png',
            onclick: function () { editFormElement(editor, url, 'action'); }
        });
        editor.addButton('plominosubform', {
            tooltip: 'Sub-form',
            image: '++resource++Products.CMFPlomino/img/PlominoForm.png',
            onclick: function () { editFormElement(editor, url, 'subform'); }
        });
        editor.addButton('plominohidewhen', {
            tooltip: 'Hidewhen',
            image: '++resource++Products.CMFPlomino/img/PlominoHideWhen.png',
            onclick: function () { editFormElement(editor, url, 'hidewhen'); }
        });
        editor.addButton('plominocache', {
            tooltip: 'Cache',
            image: '++resource++Products.CMFPlomino/img/PlominoCache.png',
            onclick: function () { editFormElement(editor, url, 'cache'); }
        });
        editor.addButton('plominopagebreak', {
            tooltip: 'Page break',
            image: '++resource++Products.CMFPlomino/img/PlominoPagebreak.png',
            onclick: function () { editFormElement(editor, url, 'pagebreak'); }
        });

        editor.onDblClick.add(function(ed, e) {
            console.debug('Double click event: ' + e.target.nodeName);
            if (top.tinyMCE.DOM.hasClass(e.target, 'plominoLabelClass')) {
                editFormElement(editor, url, 'label');
            } else if (top.tinyMCE.DOM.hasClass(e.target, 'plominoFieldClass')) {
                editFormElement(editor, url, 'field');
            } else if (top.tinyMCE.DOM.hasClass(e.target, 'plominoActionClass')) {
                editFormElement(editor, url, 'action');
            } else if (top.tinyMCE.DOM.hasClass(e.target, 'plominoHidewhenClass')) {
                editFormElement(editor, url, 'hidewhen');
            } else if (top.tinyMCE.DOM.hasClass(e.target, 'plominoSubformClass')) {
                editFormElement(editor, url, 'subform');
            };
        });

    });

    var insert_element = function(type, value, option) {

		var ed = top.tinymce.activeEditor;

        var container = "span";

		if (type == 'action') {
			var plominoClass = 'plominoActionClass';
        }
        else if (type == 'field') {
			var plominoClass = 'plominoFieldClass';
            container = "div";
        }
        else if (type == 'subform') {
			var plominoClass = 'plominoSubformClass';
            container = "div";
        }
		else if (type == 'label') {
			var plominoClass = 'plominoLabelClass';
			if (option == '0') {
				container = "span";
			} else {
                container = "div";
            }
		}
        if (type == 'label') {
            // Handle labels - TODO: replace this with example_wiget
            title = (value[0].toUpperCase() + value.slice(1, value.length)).split('-').join(" ");
            var selection = ed.selection.getNode();
            if (container == "span") {
                content = '<span class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'">'+title+'</span><br />';
            } else {
                if (top.tinymce.DOM.hasClass(selection, "plominoLabelClass") && selection.tagName === "SPAN") {
                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'"><div class="plominoLabelContent mceEditable">'+title+'</div></div><br />';
                }
                else if (top.tinymce.DOM.hasClass(selection.firstChild, "plominoLabelContent")) {
                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'">'+selection.innerHTML+'</div><br />';
                } else {
                    if (selection.textContent == "") {
                        content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'"><div class="plominoLabelContent mceEditable">'+title+'</div></div><br />';
                    } else {
                        content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'"><div class="plominoLabelContent mceEditable">'+ed.selection.getContent()+'</div></div><br />';
                    }
                }
            }
            ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});
        }
		else if (plominoClass !== undefined)
		{
            $.ajax({
                url: '@@tinyform/example_widget?widget_type='+type+'&id='+value,
                success: function(example) {
                    // example is now a JSON string
                    // example = $(example).last().html();
                    // tinymce will remove a span around a block element since its invalid
                    if ($(example).find("div,table,p").length) {
                        container = "div";
                    }
                    if (example != undefined) {
                        var span = '<'+container+' class="'+plominoClass
                            + ' mceNonEditable" data-mce-resize="false" data-plominoid="'+value+'">'
        //                    +'<span class="plominoEditWidgetTab">'+  value+'</span>'
                            + example + '</'+container+'><br />';
                    }
                    else {
                        // String to add in the editor
                        var span = '<span class="' + plominoClass + '">' + value + '</span><br />';
                    }

                    // Insert or replace the selection

                    // TinyMCE 3, still needed ?
                    //tinyMCEPopup.restoreSelection();
                    var selection = ed.selection.getNode();
                    if (top.tinymce.DOM.hasClass(selection, 'plominoActionClass') || top.tinymce.DOM.hasClass(selection, 'plominoFieldClass') || top.tinymce.DOM.hasClass(selection, 'plominoLabelClass') || top.tinymce.DOM.hasClass(selection, 'plominoSubformClass'))
                        ed.execCommand('mceInsertContent', false, span, {skip_undo : 1});
                    else
                        ed.execCommand('mceInsertContent', false, span, {skip_undo : 1});
                }
            });
		}
		else if (type == "hidewhen" || type == 'cache')
		{
			// Insert or replace the selection

            // TinyMCE 3, still needed ?
			//tinyMCEPopup.restoreSelection();


            var cssclass = 'plomino' + type.charAt(0).toUpperCase() + type.slice(1) + 'Class';

			// Select the parent node of the selection
			var selection = ed.selection.getNode();
			// If the node is a <span class="plominoFieldClass"/>, select all its content
			if (top.tinymce.DOM.hasClass(selection, cssclass))
			{
				// get the old hide-when id
                var oldId = selection.getAttribute('data-plominoid');
                var pos = selection.getAttribute('data-plomino-position')

				// get a list of hide-when opening and closing spans
				var hidewhens = ed.dom.select('span.'+cssclass);
				// find the selected span
				var i;
				for (i = 0; i < hidewhens.length; i++) {
					if (hidewhens[i] == selection)
						break;
				}

				// change the corresponding start/end
				if (pos == 'start') {
					selection.setAttribute('data-plominoid', value);

					for (; i < hidewhens.length; i++) {
						if (hidewhens[i] && hidewhens[i].getAttribute('data-plominoid') == oldId &&
                            hidewhens[i].getAttribute('data-plomino-position') == 'end') {
							hidewhens[i].setAttribute('data-plominoid', value);
							break;
						}
					}
				}
				// change the corresponding start by going backwards
				else {
					selection.setAttribute('data-plominoid', value);

					for (; i >= 0; i--) {
						if (hidewhens[i] && hidewhens[i].getAttribute('data-plominoid') == oldId &&
                            hidewhens[i].getAttribute('data-plomino-position') == 'start') {
							hidewhens[i].setAttribute('data-plominoid', value);
							break;
						}
					}
				}
			}

			else {
				// String to add in the editor
				var zone = '<span class="'+cssclass+' mceNonEditable" data-plominoid="'+value+'" data-plomino-position="start">&nbsp;</span>' +
                    ed.selection.getContent() +
                    '<span class="'+cssclass+' mceNonEditable" data-plominoid="'+value+'" data-plomino-position="end">&nbsp;</span><br />';
				ed.execCommand('mceInsertContent', false, zone, {skip_undo : 1});
			}
		}

	};



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
            // var elementEditionPage = '++add++PlominoField';
            var elementIdName = 'fieldid';
        }
        else if (elementType === "label") {
            var elementClass = 'plominoLabelClass';
            var elementEditionPage = '@@tinymceplominoform/label_form';
            var elementIdName = 'labelid';
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
        else if (elementType === "pagebreak") {
            // Insert the page break straight away
            ed.execCommand('mceInsertContent', false, '<hr class="plominoPagebreakClass"><br />');
            return;
        }
        else
            return;

        // Find the element id
        // Select the parent node of the selection
        var selection = ed.selection.getNode();
        var customText = false;
        if (elementType === "label") {
            if (tinymce.DOM.hasClass(selection, 'plominoLabelContent')) {
                selection = selection.parentNode;
                var customText = true;
            } else if (selection.tagName === "DIV" && tinymce.DOM.hasClass(selection, "plominoLabelClass")) {
                var customText = true;
            }
        }
        // If the node is a <span class="plominoFieldClass"/>, select all its content
        if (tinymce.DOM.hasClass(selection, elementClass))
        {
            ed.selection.select(selection);
            var elementId = selection.getAttribute('data-plominoid');
            if (elementId == null) {
                elementId = selection.firstChild.nodeValue;
                // hide-when and cache zones start with start:id and finish with end:id
                if (elementType === "hidewhen" || elementType === "cache")
                {
                    var splittedId = elementId.split(':');
                    if (splittedId.length > 1)
                        elementId = splittedId[1];
                }
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
        // Trim whitespace from the start/end
        elementId = elementId.trim();

        if (customText) {
            elementId = elementId + ':1'
        }
        var base_url = $('body').attr('data-base-url');
        var edurl = base_url + '/' + elementEditionPage + '?' + elementIdName + '=' + elementId + '&ajax_load=1&ajax_include_head=1';
        if (elementEditionPage.indexOf('++add++')>=0 && elementId) {
            edurl = base_url + '/' + elementId + '/edit?ajax_load=1&ajax_include_head=1';
        }

        var win = ed.windowManager.open({
            url: edurl,
            width : 600 + parseInt(ed.getLang('plomino_tinymce.delta_width', 0)),
            //height : 700 + parseInt(ed.getLang('plomino_tinymce.delta_height', 0)),
            height: $(window.top).height() -50, // important so modals allow scrolling properly
            inline : "no",
            scrollbars: "no",
            resizable: "no"
        }, {
            plugin_url : url
        });

        function getParameterByName(name, url) {
            if (!url) url = window.location.href;
            name = name.replace(/[\[\]]/g, "\\$&");
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, " "));
        }

        // Whenever the settings are saved update the field in the layout
        win.$el.find('iframe').on("load", function() {

            var iframe = win.$el.find('iframe')[0];


            var doc = iframe.contentDocument || iframe.contentWindow.document;
            var jqdoc = $(doc).contents();
            // resize the popop so it fits the content
            //'height',jqdoc.find('body').height()+'px');
            //'height',jqdoc.find('body').height()+'px');
            //win.$el.find('.mce-window-body').resizeToContent();
            //win.resizeTo(600,jqdoc.find('body').height()-50);
            //win.$el.find('.mce-window-body').css('height', jqdoc.find('body').height()+'px');

            //var issaved = $(doc).contents().find(".portalMessage.info");
            // should contain "Changes saved" or "Changes cancelled"
            //TODO: get rid of valid_page and use ajax_success instead
            if (doc.location.pathname.endsWith('/valid_page')) {
                var type = getParameterByName('type', doc.location.href);
                var value = getParameterByName('value', doc.location.href);
                var option = getParameterByName('option', doc.location.href);
                insert_element(type, value, option);
                win.close();
            }
            else if (jqdoc.find('*:contains("ajax_cancelled")').length) {
                win.close();
            }
            else if (jqdoc.find('*:contains("ajax_success")').length) {
                if (elementId == "") {
                    elementId = getParameterByName('id', doc.location.href);
                }
                insert_element(elementType, elementId);
                win.close();
            }
        });

        ed.on('OpenWindow', function() {
            //alert("need to hook into url change")

        });
        win.on('close', function() {
            //alert("close")

        });

    };
})();