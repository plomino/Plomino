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
    document.getElementById(field_id+'_gridvalue').value=$.toJSON(newvalue);
}

function make_selectable(table, field_id) {
    $("#"+field_id+"_datagrid").click(function(event) {
        $(table.fnSettings().aoData).each(function (){
            $(this.nTr).removeClass('datagrid_row_selected');
        });
        $(event.target.parentNode).addClass('datagrid_row_selected');
    });
}