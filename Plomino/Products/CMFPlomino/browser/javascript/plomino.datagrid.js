jq(function(){
    jq("a.add-row").prepOverlay({
        subtype:'ajax',
        urlmatch:'$', urlreplace:' #region-content>*',
        formselector:'[id=plomino_form]',
        noform: 'close',
        config:{closeOnClick: false},
        closeselector:'[name=plomino_close]',
        afterpost: function(data, data_parent) {
        	 errors = data.context.querySelector('[id=error_list]');
        	 if(errors) {
        		 alert(errors.textContent);
        	 }
	    	 field_id = data.context.querySelector('[id=plomino_parent_field]').innerHTML;
	     	 raw = data.context.querySelector('[id=raw_values]').innerHTML;
	         eval("table=window."+field_id+"_datatable;");
	     	 len = table.fnSettings().aoColumns.length
	         newrow = new Array();
	     	 fields=data.context.querySelectorAll('span[plomino]')
	         for(i=0;i<len;i++) {
	             newrow[i] = fields[i].innerHTML;
	         }
	         table.fnAddData( newrow );
	         currentjson = document.getElementById(field_id+'_gridvalue').value
	         current = $.evalJSON(currentjson);
	         current.push($.evalJSON(raw));
	         document.getElementById(field_id+'_gridvalue').value=$.toJSON(current);
	         document.getElementById(field_id+'_editrow').style.display = "inline";
	         document.getElementById(field_id+'_deleterow').style.display = "inline";
        }
    });
});

function fnGetSelected( oTableLocal )
{
    var aReturn = new Array();
    var aTrs = oTableLocal.fnGetNodes();
    j = -1;
    for ( var i=0 ; i<aTrs.length ; i++ )
    {
        if ( $(aTrs[i]).hasClass('datagrid_row_selected') )
        {
            aReturn.push( aTrs[i] );
            j = i;
        }
    }
    return [aReturn, j];
}

function datagrid_delete(table, field_id) {
	selection = fnGetSelected(table);
    var anSelected=selection[0];
    table.fnDeleteRow(anSelected[0], function(){}, true);
    currentjson = document.getElementById(field_id+'_gridvalue').value
    current = $.evalJSON(currentjson);
    newvalue = new Array();
    for(i=0;i<current.length;i++) {
    	if(i!=selection[1]) {
    		newvalue.push(current[i]);
    	}
    }
    if(newvalue.length==0) {
        document.getElementById(field_id+'_editrow').style.display = "none";
        document.getElementById(field_id+'_deleterow').style.display = "none";
    }
    document.getElementById(field_id+'_gridvalue').value=$.toJSON(newvalue);
}

function get_current_row(table, field_id) {
	selection = fnGetSelected(table);
    var anSelected=selection[0];
    currentjson = document.getElementById(field_id+'_gridvalue').value
    current = $.evalJSON(currentjson);
    row = current[selection[1]];
    return $.toJSON(row);
}
function make_selectable(table, field_id) {
    $("#"+field_id+"_datagrid").click(function(event) {
        $(table.fnSettings().aoData).each(function (){
            $(this.nTr).removeClass('datagrid_row_selected');
        });
        $(event.target.parentNode).addClass('datagrid_row_selected');
        
        rowdata = get_current_row(table, field_id);
        jq("#"+field_id+"_editrow").removeAttr('rel');
        jq("#"+field_id+"_editrow").prepOverlay({
            subtype:'ajax',
            urlmatch:'$', urlreplace:"&Plomino_datagrid_rowdata=" + $.URLEncode(rowdata) +' #region-content>*',
            formselector:'[id=plomino_form]',
            noform: 'close',
            config:{closeOnClick: false},
            closeselector:'[name=plomino_close]',
            afterpost: function(data, data_parent) {
            	errors = data.context.querySelector('[id=error_list]');
           	    if(errors) {
           		   alert(errors.textContent);
           	    }
        	  field_id = data.context.querySelector('[id=plomino_parent_field]').innerHTML;
         	  raw = data.context.querySelector('[id=raw_values]').innerHTML;
         	  eval("table=window."+field_id+"_datatable;");
         	 len = table.fnSettings().aoColumns.length
             newrow = new Array();
         	 fields=data.context.querySelectorAll('span[plomino]')
             for(i=0;i<len;i++) {
                 newrow[i] = fields[i].innerHTML;
             }
         	 selection = fnGetSelected(table)[1];
         	 table.fnUpdate(newrow, selection);
             currentjson = document.getElementById(field_id+'_gridvalue').value
             current = $.evalJSON(currentjson);
             current[selection]=$.evalJSON(raw);
             document.getElementById(field_id+'_gridvalue').value=$.toJSON(current);
            }
        });
    });
}