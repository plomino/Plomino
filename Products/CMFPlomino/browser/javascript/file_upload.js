jQuery(function() {
    if (typeof jQuery.prototype.fileupload == 'function') {
        // Install collective.upload to enable ajax file upload in Plomino
        jQuery('#plomino_form input[type="file"]').fileupload({
            dataType: 'json',
            'url': 'upload_to_session',
            add: function(e, data) {
                console.log(data);
                data.progress = jQuery('<div/>').addClass('progress');
                progress_bar = jQuery('<div/>').addClass('bar');
                data.progress.append(progress_bar);
                data.context = jQuery('<p/>').text('Uploading ' +
                    data.files[0].name + ' ' + data.files[0].size/1000 + ' kb');
                data.context.insertAfter(this);
                data.progress.insertAfter(this);
                data.submit();
            },
            done: function (e, data) {
                var container = jQuery(this).parent();
                var hidden_name = "_uploaded_in_session_" + data.fileInput.attr('name');
                var node = jQuery("<input type='hidden'/>").attr('name', hidden_name).attr('value', data.result.file_id);
                container.append(node);
                data.progress.detach();
                data.context.detach();
                container.append(jQuery("<div>").addClass('upload-status').text(data.files[0].name + " uploaded"))
                if (! container.find("input[name=_has_session_uploads]").length) {
                    container.append(jQuery("<input type='hidden' name='_has_session_uploads', value='yes'>"));
                }
            },
            progress: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                var container = jQuery(this).parent();
                container.find('.progress .bar').css('width', progress + '%');
            }

        });
    }
});

