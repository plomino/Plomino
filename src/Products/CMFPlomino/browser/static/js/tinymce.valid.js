// Functions called by the popup
var PlominoDialog = {
	// Called when the "submit" button is clicked
	submit : function(type, value, option) {

		var ed = top.tinymce.activeEditor;

		if (type == 'action')
			var plominoClass = 'plominoActionClass';
		else if (type == 'field')
			var plominoClass = 'plominoFieldClass';
		else if (type == 'subform')
			var plominoClass = 'plominoSubformClass';
		else if (type == 'label') {
			var plominoClass = 'plominoLabelClass';
			if (option != null && option.length > 0) {
				value = value + ':' + option;
			}
		}

		if (plominoClass !== undefined)
		{
            var example = document.getElementById("example_widget").innerHTML;
            if (example) {
                var span = '<span class="'+plominoClass
                    + ' mceNonEditable" data-plominoid="'+value+'">'
//                    +'<span class="plominoEditWidgetTab">'+  value+'</span>'
                    + example + '</span>';
            }
            else {
                // String to add in the editor
                var span = '<span class="' + plominoClass + '">' + value + '</span>';
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
		else if (type == "hidewhen" || type == "label" || type == 'cache')
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
				var zone = '<span class="'+cssclass+' mceNonEditable" data-plominoid="'+value+'" data-plomino-position="start"></span>' +
                    ed.selection.getContent() +
                    '<span class="'+cssclass+' mceNonEditable" data-plominoid="'+value+'" data-plomino-position="end"></span>';
				ed.execCommand('mceInsertContent', false, zone, {skip_undo : 1});
			}
		}

		if (type !== "field")
			top.tinymce.activeEditor.windowManager.close();
	}
}