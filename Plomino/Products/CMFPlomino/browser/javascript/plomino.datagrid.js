/*
 * Author: Romaric BREIL <romaric.breil@supinfo.com>
 * 
 * Those functions allow to manage Plomino datagrid fields.
 */

/*
 * Displays the form (obtained by an AJAX request), and integrates it in the page.
 * - field_id: id of the datagrid field
 * - formurl: url of the form
 * - onsubmit(newrow): function called when the server returned the result of the
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
			jq.get(this.action, jq(this).serialize(), function(data, textStatus, XMLHttpRequest){
				// Call back function with new row
				var rowdata = new Array();
				jq('span[plomino]', data).each(function(){
					rowdata.push(this.innerHTML);
				})
				onsubmit(rowdata);
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
 * Update the field used to send data to the server.
 * - field_id: id of the datagrid field
 * - data: 2d data array
 */
function datagrid_update_field(field_id, data) {
	for (var i = 0; i < data.length; i++) {
		if (data[i] === null) {
			data.splice(i, 1);
			i--;
		}
	}
    document.getElementById(field_id+'_gridvalue').value=jq.toJSON(data);
}

/*
 * Adds a row to the datagrid, calling datagrid_show_form().
 * - table: JQuery DataTables object (returned by the initialisation method)
 * - field_id: id of the datagrid field
 * - formurl: url of the form used to insert data
 */
function datagrid_add_row(table, field_id, formurl) {
	datagrid_show_form(field_id, formurl, function(rowdata) {
		table.fnAddData(rowdata);
		datagrid_update_field(field_id, table.fnGetData());
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
		formurl += '&Plomino_datagrid_rowdata=' + jq.toJSON(table.fnGetData(row));
		datagrid_show_form(field_id, formurl, function(rowdata) {
			table.fnUpdate(rowdata, row);
			datagrid_update_field(field_id, table.fnGetData());
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
		table.fnDeleteRow(row, undefined, true);
		datagrid_update_field(field_id, table.fnGetData());
	}
	else {
		alert('You must select a row to delete.');
	}
}
