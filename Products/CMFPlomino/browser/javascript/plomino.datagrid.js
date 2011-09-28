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
 *  	form (second request, when the user clicks on the submit button of the sub-form)
 */
function datagrid_show_form(field_id, formurl, onsubmit) {
	jq("#" + field_id + "_editform").load(formurl + ' #plomino_form', function() {
		var editform = jq(this);
		var popup = jq(this);
		// Edit-form close button
		jq("input[name=plomino_close]", this).removeAttr('onclick').click(function() {
			popup.dialog('close');
		});
		// Edit form submission
		jq('form', editform).submit(function(){
			var message = "";

			jq.ajax({url: this.action+"?"+jq(this).serialize(),
				async: false,
				//context: jq('#plomino_form'),
				error: function() {
					alert("Error while validating.");
				},
				success: function(data) {
					message = jq(data).filter('#plomino_child_errors').html();
					return false;
				}
			});
			
			if(!(message == null || message=='')) {
				alert(message);
				return false;
			}
			jq.get(this.action, jq(this).serialize(), function(data, textStatus, XMLHttpRequest){
				// Call back function with new row
				var rowdata = new Array();
				jq('span.plominochildfield', data).each(function(){
					rowdata.push(this.innerHTML);
				})
				var raw = jq.evalJSON(jq('#raw_values', data).text());
				onsubmit(rowdata, raw);
			});
			popup.dialog('close');
			return false;
		});
		// Prepare and display the dialog
		jq('.documentActions', editform).remove();
		popup.dialog("option", "title", jq('.documentFirstHeading', editform).remove().text());
		popup.dialog('open');
	});
}

/*
 * Deselect every rows.
 * - table: JQuery DataTables object (returned by the initialisation method)
 */
function datagrid_deselect_rows(table) {
	var rows = table.fnGetNodes();
	for (var i = 0; i < rows.length; i++) {
		var row = rows[i];
		if (row)
			jq(row).removeClass('datagrid_row_selected');
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
		if (row && jq(row).hasClass('datagrid_row_selected'))
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
		// update the datagrid
		table.fnAddData(rowdata);

		// update the field
		var field = jq('#' + field_id + '_gridvalue');
		var field_data = jq.evalJSON(field.val());
		field_data.push(raw);
		field.val(jq.toJSON(field_data));

		// show buttons
		jq('#' + field_id + '_editrow').show();
		jq('#' + field_id + '_deleterow').show();
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
		var field = jq('#' + field_id + '_gridvalue');
		var field_data = jq.evalJSON(field.val());
		var row_index = datagrid_get_field_index(table, row);
		formurl += '&Plomino_datagrid_rowdata=' + jq.URLEncode(jq.toJSON(field_data[row_index]));
		datagrid_show_form(field_id, formurl, function(rowdata, raw) {
			// update the datagrid
			table.fnUpdate(rowdata, row);

			// update the field
			field_data[row_index] = raw;
			field.val(jq.toJSON(field_data));
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
		var row_index = datagrid_get_field_index(table, row)

		// delete the row in the datagrid
		table.fnDeleteRow(row, undefined, true);

		// update the field
		var field = jq('#' + field_id + '_gridvalue');
		var field_data = jq.evalJSON(field.val());
		field_data.splice(row_index, 1);
		field.val(jq.toJSON(field_data));
	}
	else {
		alert('You must select a row to delete.');
	}
}
