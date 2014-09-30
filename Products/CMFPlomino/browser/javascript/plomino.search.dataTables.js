/* Set the defaults for DataTables initialisation */
$.extend( true, $.fn.dataTable.defaults, {
    //"sDom": "<'row-fluid'<'span6'><'span6'>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>",
    "sDom": "<'row-fluid'<'span12'>r>t<'row-fluid'<'span3'l><'span4'i><'span5'p>>",
    "sPaginationType": "bootstrap",

"fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ){
    $(nRow).addClass('linkToDocument');
    
    $(nRow).bind('click',function(){
        var dburl = $('#Plomino_Database_URL').val();
        window.location= dburl + '/' + aData[0];
    });
},
    "sServerMethod":"POST",
    'fnServerParams':function(aoData){
        var form_query = {};
        jQuery.each(jQuery('.staticSearch'),function(){
            
            var query = jQuery(this).serializeZopeQuery();
            form_query = jQuery.extend(form_query,query);
        });
        aoData.push({name:'query', value: JSON.stringify(form_query)});
     },
    'fnServerData': function ( sSource, aoData, fnCallback, oSettings ) {
     oSettings.jqXHR = jQuery.ajax( {
        'dataType': 'json',
        'type': 'POST',
        'url': sSource,
        'data': aoData,
        'success': fnCallback
      } );
    },
    "oLanguage": {
        "sUrl": "@@collective.js.datatables.translation"
    }
});
var plominoSearchTables = new Array();
$(document).ready(function(){
    $('.dynamicSearch').bind('change',function(event){
        jQuery.each(plominoSearchTables,function(k,table){
            jQuery('#'+table).dataTable().fnDraw();
        });
    });
    $('#avanzata_opt-avanzata').bind('click',function(){
        $('#advancedSearchDiv').toggle();
    });
});