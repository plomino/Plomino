/*
 * Author: Romaric BREIL <romaric.breil@supinfo.com>
 *
 * Those functions allow to manage Plomino datagrid fields.
 */

/*
 * Displays the form (obtained by an AJAX request), and integrates it in the page.
 * - field_id: id of the datagrid field
 * - formurl: url of the form
 * - onsubmit(newrow, rawdata): function called when the server returned the result of the
 *   form (second request, when the user clicks on the submit button of the sub-form)
 */
function datagrid_show_form(field_id, formurl, onsubmit) {
	var field_selector = "#" + field_id + "_editform";
	$(field_selector).html(
		'<iframe name="' + field_id + '_iframe" style="height:100%;width:100%" height="100%" width="100%"></iframe>'
	);
	var iframe = $("#" + field_id + "_editform iframe");
	iframe.attr('src', formurl);
	iframe.load(function() {
		var popup = $(field_selector);
		var body = iframe[0].contentDocument.body;
		// Edit-form close button
		$("input[name=plomino_close]", body).removeAttr('onclick').click(function() {
			popup.dialog('close');
		});
		// Edit form submission
		$('form', body).submit(function(){
			var message = "";

			$.ajax({url: this.action+"?"+$(this).serialize(),
				async: false,
				//context: $('#plomino_form'),
				error: function() {
					alert("Error while validating.");
				},
				success: function(data) {
					message = $(data).filter('#plomino_child_errors').html();
					return false;
				}
			});

			if(!(message === null || message === '')) {
				alert(message);
				// Avoid Plone message "You already submitted this form", since we didn't
				jQuery(this).find('input[type="submit"].submitting').removeClass('submitting');
				return false;
			}
			$.get(this.action, $(this).serialize(), function(data, textStatus, XMLHttpRequest){
				// Call back function with new row
				var rowdata = [];
				$('span.plominochildfield', data).each(function(){
					rowdata.push(this.innerHTML);
				});
				var raw = $.evalJSON($('#raw_values', data).text());
				onsubmit(rowdata, raw);
			});
			popup.dialog('close');
			return false;
		});
		// Prepare and display the dialog
		$('.documentActions', body).remove();
		popup.dialog("option", "title", $('.documentFirstHeading', body).remove().text());
		var table = $("#" + field_id + "_datagrid");
		var options = table.dataTable().fnSettings().oInit;
		if(options.plominoDialogOptions) {
			keys = Object.keys(options.plominoDialogOptions);
			for(var k in keys) {
				popup.dialog("option", keys[k], options.plominoDialogOptions[keys[k]]);
			}
		}
		popup.dialog('open');
	});
}

/*
 * Deselect all rows.
 * - table: JQuery DataTables object (returned by the initialisation method)
 */
function datagrid_deselect_rows(table) {
	var rows = table.fnGetNodes();
	for (var i = 0; i < rows.length; i++) {
		var row = rows[i];
		if (row)
			$(row).removeClass('datagrid_row_selected');
	}
}

/*
 * Get the row node selected by the user.
 * - table: JQuery DataTables object (returned by the initialisation method)
 */
function datagrid_get_selected_row(table) {
	var rows = table.fnGetNodes();
	for (var i = 0; i < rows.length; i++) {
		var row = rows[i];
		if (row && $(row).hasClass('datagrid_row_selected'))
			return row;
	}
	return null;
}

/*
 * Get the correct index of the row in the field.
 * Since DataTables don't really delete rows when asked (it just set them to null, if required),
 * indexes of the datatable and the field are not identical, and must be corrected, by substracting
 * every 'null' row to the index given by the datagrid.
 *
 * - table: JQuery DataTables object (returned by the initialisation method)
 * - row: row we are searching for the index
 */
function datagrid_get_field_index(table, row) {
	// find the correct index of the row in the field
	var table_data = table.fnGetData();
	var row_index = table.fnGetPosition(row);
	var empty_rows = 0;
	for (var i = 0; i < row_index; i++)
		if (!table_data[i])
			empty_rows++;

	return row_index - empty_rows;
}

/*
 * Adds a row to the datagrid, calling datagrid_show_form().
 * - table: JQuery DataTables object (returned by the initialisation method)
 * - field_id: id of the datagrid field
 * - formurl: url of the form used to insert data
 */
function datagrid_add_row(table, field_id, formurl) {
	datagrid_show_form(field_id, formurl, function(rowdata, raw) {
		// update the field
		var field = $('#' + field_id + '_gridvalue');
		var field_data = $.evalJSON(field.val());
		field_data.push(raw);
		field.val($.toJSON(field_data));

		// show buttons
		$('#' + field_id + '_editrow').show();
		$('#' + field_id + '_deleterow').show();

		// update the datagrid
		table.fnAddData(rowdata);
	});
}

/*
 * Update a row to the datagrid, calling datagrid_show_form().
 * - table: JQuery DataTables object (returned by the initialisation method)
 * - field_id: id of the datagrid field
 * - formurl: url of the form used to update data
 */
function datagrid_edit_row(table, field_id, formurl) {
	var row = datagrid_get_selected_row(table);
	if (row) {
		// get data to send
		var field = $('#' + field_id + '_gridvalue');
		var field_data = $.evalJSON(field.val());
		var row_index = datagrid_get_field_index(table, row);
		formurl += '&Plomino_datagrid_rowdata=' + $.URLEncode($.toJSON(field_data[row_index]));
		datagrid_show_form(field_id, formurl, function(rowdata, raw) {
			// update the field
			field_data[row_index] = raw;
			field.val($.toJSON(field_data));

			// update the datagrid
			table.fnUpdate(rowdata, row);
		});
	}
	else {
		alert('You must select a row to edit.');
	}
}

/*
 * Delete a row to the datagrid.
 * - table: JQuery DataTables object (returned by the initialisation method)
 * - field_id: id of the datagrid field
 */
function datagrid_delete_row(table, field_id) {
	var row = datagrid_get_selected_row(table);
	if (row) {
		// find the correct index of the row in the field
		var row_index = datagrid_get_field_index(table, row);

		// update the field
		var field = $('#' + field_id + '_gridvalue');
		var field_data = $.evalJSON(field.val());
		field_data.splice(row_index, 1);
		field.val($.toJSON(field_data));

		// delete the row in the datagrid
		table.fnDeleteRow(row, undefined, true);
	}
	else {
		alert('You must select a row to delete.');
	}
}
