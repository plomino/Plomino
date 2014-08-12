(function ($) {

    function refreshHidewhen() {
        var onsuccess = function(data, textStatus, xhr) {
            for (var hw in data)
                $('.hidewhen-' + hw).css('display', data[hw]?'none':'block');
        }
        
        $.ajax({
            type: 'POST',
            url: 'computehidewhens',
            data: $(this).closest('form').serialize(),
            success: onsuccess,
            dataType: 'json' 
        });
    }

    $(document).on('change', "[data-dhw = 1]", refreshHidewhen);


})(jQuery);