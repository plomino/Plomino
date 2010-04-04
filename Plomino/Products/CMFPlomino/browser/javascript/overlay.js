jq(function(){
    jq("a.add-row").prepOverlay({
        subtype:'ajax',
        urlmatch:'$', urlreplace:' #region-content>*',
        formselector:'[id=plomino_form]',
        noform: 'close',
        closeselector:'[name=plomino_close]',
        afterpost: function(data, data_parent) {
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
        }
    });
});