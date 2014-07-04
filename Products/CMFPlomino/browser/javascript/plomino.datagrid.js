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

            if(!(typeof message === "undefined" || message === null || message === '')) {
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
            Object.keys = Object.keys || ie8_object_keys();
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
        var json = $.toJSON(field_data[row_index]);
        json = json.replace(/[\u007f-\uffff]/g,
            function(c) { 
                return '\\u'+('0000'+c.charCodeAt(0).toString(16)).slice(-4);
            }
        );
        formurl += '&Plomino_datagrid_rowdata=' + $.URLEncode(json);
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

/*
 * IE8 does not support Object.keys.
 * Function from here:
 * http://whattheheadsaid.com/2010/10/a-safer-object-keys-compatibility-implementation
 */
function ie8_object_keys () {
    var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !{toString:null}.propertyIsEnumerable("toString"),
        DontEnums = [
            'toString',
            'toLocaleString',
            'valueOf',
            'hasOwnProperty',
            'isPrototypeOf',
            'propertyIsEnumerable',
            'constructor'
        ],
        DontEnumsLength = DontEnums.length;

    return function (o) {
        if (typeof o != "object" && typeof o != "function" || o === null)
            throw new TypeError("Object.keys called on a non-object");

        var result = [];
        for (var name in o) {
            if (hasOwnProperty.call(o, name))
                result.push(name);
        }

        if (hasDontEnumBug) {
            for (var i = 0; i < DontEnumsLength; i++) {
                if (hasOwnProperty.call(o, DontEnums[i]))
                    result.push(DontEnums[i]);
            }
        }

        return result;
    };
}

/*
 * Inline Editing : compute row as inline Form.
 * - oTable: JQuery DataTables object (returned by the initialisation method)
 * - field_id : field_id to get raw values
 * - formul : url to get edit fields 
 */
function datagrid_edit_inline_form( oTable, field_id, formurl )
{
	var nRow = datagrid_get_selected_row(oTable);
	if ( nRow ) {
		var jqTds = $('>td', nRow);
		var row_index = oTable.fnGetPosition(nRow)	

		var field_data = $.evalJSON( $('#' + field_id + '_gridvalue').val() );
		var row_data = field_data[row_index];
		
		formurl += '&Plomino_datagrid_rowdata=' + $.URLEncode($.toJSON(row_data));

		$.getJSON( formurl, function( data ) 
		{
			for (var i = 0; i < data.length; i++) {
				 $( jqTds[i] ).html( data[i] );
			};
			jqTds[jqTds.length-1].innerHTML += "<button class='save' href='#' >Save</button>   <button class='cancel' href='#'>Cancel</button>";
		});
	}
	else {
		alert('You must select a row to edit.');
	}
	return nRow;
}

/*
 * Inline Editing  : save the row.
 * - oTable: JQuery DataTables object (returned by the initialisation method)
 * - nRow : row
 * - field_id : field id of the datagrid Field
 * - form_url : url to use for Ajax
 */
function datagrid_save_inline_row ( oTable, nRow, field_id, form_url ) {

	var jqFields = $('input,textarea,select',nRow);
	var jqTds = $('>td', nRow);
	var url = form_url+"&"+jqFields.serialize();

	$.get(url,function(data)
	{
		message = $(data).filter('#plomino_child_errors').html();
		if(message===null || message==='')
		{
			var row_index = oTable.fnGetPosition(nRow)
			
			// from response
			var row_data = $('span.plominochildfield', data).map(function(d,el){ return el.innerHTML });
			var raw_values = $.evalJSON($('#raw_values', data).html().trim());
			
			//update field_data
			var field = $('#' + field_id + '_gridvalue');
			var field_data= $.evalJSON(field.val());
			field_data[row_index] = $.evalJSON($('#raw_values', data).html().trim());
			field.val($.toJSON(field_data));

			//update datatable
			for (var i=0;i<row_data.length;i++) {
				var cell_data =  row_data[i];
				if(cell_data.replace("\n","").trim()!="" && $(cell_data)!=null && $(cell_data).hasClass('TEXTFieldRead-TEXTAREA')) {
					cell_data = $(cell_data).html();			  	
				}
				oTable.fnUpdate( cell_data, nRow, i, false );
			} 
			
			oTable.fnDraw();
			return true;
		}
		else
		{
			alert(message);
			return false;
		}
	});
}

/*
 * Inline Editing : add form with empty values to the datagrid.
 * - oTable: JQuery DataTables object (returned by the initialisation method)
 * - fields : needed fields to render the form 
 */
function datagrid_add_inline_row( oTable, fields) {

	var aiNew = oTable.fnAddData( [ fields.map(function(){ return '' }) ] );
	var nRow = oTable.fnGetNodes( aiNew[0] );
	var jqTds = $('>td', nRow);
	for ( var i=0, iLen=jqTds.length ; i<iLen ; i++ ) {
		$(jqTds[i]).html(fields[i]);
	}
	jqTds[jqTds.length-1].innerHTML += "<button class='save' href='#' >Enter</button>   <button class='cancel' href='#'>Cancel</button>";
	return nRow;

}

/*
 * Inline Editing : restore row as a normal datatable row.
 * - oTable: JQuery DataTables object (returned by the initialisation method)
 * - nRow : row
 */
function datagrid_restore_row( oTable, nRow ) {

	function isEmpty(data){
		for (var i = 0; i < data.length; i++) {
			if(data[i]!="") return false;
		}
		return true;
	}

	var aData = oTable.fnGetData(nRow);
	if (aData) {
	if ( isEmpty(aData) ) { oTable.fnDeleteRow(nRow) }
	else {
		var jqTds = $('>td', nRow);
		for ( var i=0, iLen=jqTds.length ; i<iLen ; i++ ) {
			oTable.fnUpdate( aData[i], nRow, i, false );
		}
	}
	}
	oTable.fnDraw();
} 
