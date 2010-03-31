jq(function(){
    jq("a.remove-record").click(function() {
        if (confirm('Do you really want to remove this record?')) {
            $self = jq(this);
            var $widget = $self.parents('.ArchetypesField-GridField');
            var url = $self.attr('href');
            jq.get(url, function() {
               var field_url = url.replace(/(.*?)\/(add|edit|delete).*/g, "$1");
               $widget.load(field_url + '/ajax_render');
            });
        }
       return false;
    });

    jq("a.edit-record").prepOverlay({
       subtype:'ajax',
       urlmatch:'$', urlreplace:'',
       formselector:'form',
       noform: 'close',
       closeselector:'[name=form.buttons.cancel]',
       afterpost: function(data, data_parent) {
           var $widget = data_parent.data('source').parents('.ArchetypesField-GridField');
           var url = data_parent.data('target');
           var field_url = url.replace(/(.*?)\/(add|edit|delete).*/g, "$1");
           $widget.load(field_url + '/ajax_render');
       }
    });
    jq("a.add-record").prepOverlay({
       subtype:'ajax',
       urlmatch:'$', urlreplace:' #content>*',
       formselector:'[id=plomino_form]',
       noform: 'close',
       closeselector:'[name=plomino_close]',
       afterpost: function(data, data_parent) {
    	   newdoc_path = data.context.querySelector('[id=plomino_path]').innerHTML;
           field_id = data.context.querySelector('[id=plomino_doclink_field]').innerHTML;
           field = document.getElementById(field_id);
           alert(field.value);
           field.value = field.value+"@"+newdoc_path;
           alert(field.value);
           children_loadSource();
       }
   });
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