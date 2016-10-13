// Functions called by the popup
var PlominoDialog = {
	// Called when the "submit" button is clicked
	submit : function(type, value, option) {

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
            // Handle labels
            var selection = ed.selection.getNode();
            if (container == "span") {
                content = '<span class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'">&nbsp;</span><br />';
            } else {
                if (top.tinymce.DOM.hasClass(selection, "plominoLabelClass") && selection.tagName === "SPAN") {
                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'"><div class="plominoLabelContent mceEditable">&nbsp;</div></div><br />';
                }
                else if (top.tinymce.DOM.hasClass(selection.firstChild, "plominoLabelContent")) {
                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'">'+selection.innerHTML+'</div><br />';
                } else {
                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="'+value+'"><div class="plominoLabelContent mceEditable">'+selection.outerHTML+'</div></div><br />';
                }
            }
            ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});
        }
		else if (plominoClass !== undefined)
		{
            var eblock = document.getElementById("example_widget");
            var example = eblock.innerHTML;
            // tinymce will remove a span around a block element since its invalid
            if (eblock.getElementsByTagName("div") ||
                eblock.getElementsByTagName("table") ||
                eblock.getElementsByTagName("p")) {
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

		if (type !== "field")
			top.tinymce.activeEditor.windowManager.close();
	}
}