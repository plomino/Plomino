jQuery(function() {
    if (typeof jQuery.prototype.fileupload == 'function') {
        // Install collective.upload to enable ajax file upload in Plomino
        jQuery('#plomino_form input[type="file"]').fileupload({
            dataType: 'json',
            'url': 'upload_to_session',
            add: function(e, data) {
                console.log(data);
                data.context = jQuery('<p/>').text('Uploading ' + data.files[0].name);
                data.context.insertAfter(this);
                data.submit();
            },
            done: function (e, data) {
                var hidden_name = "_uploaded_in_session_" + data.fileInput.attr('name');
                var node = jQuery("<input type='hidden'/>").attr('name', hidden_name).attr('value', data.result.file_id);
                data.context.text(data.files[0].name);
                data.context.append(node);
                if (! data.context.find("input[name=_has_session_uploads").length) {
                    data.context.append(jQuery("<input type='hidden' name='_has_session_uploads', value='yes'>"))
                }
            }
        });
    }
});

