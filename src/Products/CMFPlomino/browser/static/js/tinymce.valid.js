// Functions called by the popup
var PlominoDialog = {
	// Called when the "submit" button is clicked
	submit : function(type, value) {

		var ed = top.tinymce.activeEditor;

		if (type == 'action')
			var plominoClass = 'plominoActionClass';
		else if (type == 'field')
			var plominoClass = 'plominoFieldClass';
		else if (type == 'subform')
			var plominoClass = 'plominoSubformClass';

		if (plominoClass !== undefined)
		{
			// String to add in the editor
			var span = '<span class="' + plominoClass + '">' + value + '</span>';

			// Insert or replace the selection

            // TinyMCE 3, still needed ?
			//tinyMCEPopup.restoreSelection();
			var selection = ed.selection.getNode();
			if (top.tinymce.DOM.hasClass(selection, 'plominoActionClass') || top.tinymce.DOM.hasClass(selection, 'plominoFieldClass') || top.tinymce.DOM.hasClass(selection, 'plominoSubformClass'))
				ed.dom.setOuterHTML(selection, span);
			else
				ed.execCommand('mceInsertContent', false, span, {skip_undo : 1});
		}
		else if (type == "hidewhen")
		{
			// Insert or replace the selection

            // TinyMCE 3, still needed ?
			//tinyMCEPopup.restoreSelection();

			// Select the parent node of the selection
			var selection = ed.selection.getNode();
			// If the node is a <span class="plominoFieldClass"/>, select all its content
			if (top.tinymce.DOM.hasClass(selection, 'plominoHidewhenClass'))
			{
				// get the old hide-when id
				var oldId = selection.firstChild.nodeValue;
				var splittedId = oldId.split(':');
				if (splittedId.length > 1)
					oldId = splittedId[1];

				// get a list of hide-when opening and closing spans
				var hidewhens = ed.dom.select('span.plominoHidewhenClass');
				// find the selected span
				var i;
				for (i = 0; i < hidewhens.length; i++) {
					if (hidewhens[i] == selection)
						break;
				}

				// change the corresponding end
				if (splittedId[0] == 'start') {
					selection.firstChild.nodeValue = 'start:' + value;

					for (; i < hidewhens.length; i++) {
						if (hidewhens[i].firstChild && hidewhens[i].firstChild.nodeValue == 'end:' + oldId) {
							hidewhens[i].firstChild.nodeValue = 'end:' + value;
							break;
						}
					}
				}
				// change the corresponding start
				else {
					selection.firstChild.nodeValue = 'end:' + value;

					for (; i >= 0; i--) {
						if (hidewhens[i].firstChild && hidewhens[i].firstChild.nodeValue == 'start:' + oldId) {
							hidewhens[i].firstChild.nodeValue = 'start:' + value;
							break;
						}
					}
				}
			}

			else {
				// String to add in the editor
				var zone = '<span class="plominoHidewhenClass">start:' + value + '</span>' + ed.selection.getContent() + '<span class="plominoHidewhenClass">end:' + value + '</span>';
				ed.execCommand('mceInsertContent', false, zone, {skip_undo : 1});
			}
		}
		else if (type == "cache")
		{
			// Insert or replace the selection

            // TinyMCE 3, still needed ?
			//tinyMCEPopup.restoreSelection();

			// Select the parent node of the selection
			var selection = ed.selection.getNode();
			// If the node is a <span class="plominoFieldClass"/>, select all its content
			if (top.tinymce.DOM.hasClass(selection, 'plominoCacheClass'))
			{
				// get the old cache id
				var oldId = selection.firstChild.nodeValue;
				var splittedId = oldId.split(':');
				if (splittedId.length > 1)
					oldId = splittedId[1];

				// get a list of cache opening and closing spans
				var caches = ed.dom.select('span.plominoCacheClass');
				// find the selected span
				var i;
				for (i = 0; i < caches.length; i++) {
					if (caches[i] == selection)
						break;
				}

				// change the corresponding end
				if (splittedId[0] == 'start') {
					selection.firstChild.nodeValue = 'start:' + value;

					for (; i < caches.length; i++) {
						if (caches[i].firstChild && caches[i].firstChild.nodeValue == 'end:' + oldId) {
							caches[i].firstChild.nodeValue = 'end:' + value;
							break;
						}
					}
				}
				// change the corresponding start
				else {
					selection.firstChild.nodeValue = 'end:' + value;

					for (; i >= 0; i--) {
						if (caches[i].firstChild && caches[i].firstChild.nodeValue == 'start:' + oldId) {
							caches[i].firstChild.nodeValue = 'start:' + value;
							break;
						}
					}
				}
			}

			else {
				// String to add in the editor
				var zone = '<span class="plominoCacheClass">start:' + value + '</span>' + ed.selection.getContent() + '<span class="plominoCacheClass">end:' + value + '</span>';
				ed.execCommand('mceInsertContent', false, zone, {skip_undo : 1});
			}
		}

		if (type !== "field")
			top.tinymce.activeEditor.windowManager.close();
	}
}