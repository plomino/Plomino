function fnGetSelected( oTableLocal )
{
    var aReturn = new Array();
    var aTrs = oTableLocal.fnGetNodes();
    
    for ( var i=0 ; i<aTrs.length ; i++ )
    {
        if ( $(aTrs[i]).hasClass('datagrid_row_selected') )
        {
            aReturn.push( aTrs[i] );
        }
    }
    return aReturn;
}
function fnClickAddRow(table, field_id) {
    len = table.fnSettings().aoColumns.length
    newrow = new Array();
    for(i=0;i<len;i++) {
        newrow[i]='';
    }
    table.fnAddData( newrow );
    make_editable(table, field_id);
}
function fnDeleteAndUpdate(table, field_id) {
    var anSelected=fnGetSelected(table);
    table.fnDeleteRow(anSelected[0], function(){}, true);
    save(table, field_id);
}

function save(table, field_id) {
    data = table.fnGetData();
    csv="";
    $(data).each(function(row) {
        r=data[row];
        if(typeof r!="undefined" && r!=null) {
            csv=csv+r.join('\t')+'\n';
        }
       });
    document.getElementById(field_id+'_gridvalue').value=csv;
}
function make_editable(table, field_id) {
    $('#'+field_id+'_datagrid tbody td').editable( function(value, settings){
        aPos = table.fnGetPosition( this );
        table.fnUpdate( value, aPos[0], aPos[1] );
        save(table, field_id);
        return value;
    }, {
        tooltip   : "Doubleclick to edit...",
        event     : "dblclick",
    });
}

function make_selectable(table, field_id) {
    $("#"+field_id+"_datagrid").click(function(event) {
        $(table.fnSettings().aoData).each(function (){
            $(this.nTr).removeClass('datagrid_row_selected');
        });
        $(event.target.parentNode).addClass('datagrid_row_selected');
    });
}