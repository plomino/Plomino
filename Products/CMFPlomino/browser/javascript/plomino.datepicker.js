
(function ($) {
    "use strict";
    function initDatePicker() {
        var value = $(this).val();
        var options = $(this).data('datepickerOptions');
        if(typeof(options)!='object') options = {};
        if ($(this).data('datepickerDateformat')&&!('dateFormat' in options)) {
            /* in case you use unusual date format not easily convertible
               between jQuery dateFormat and python datetime format */
            options['dateFormat'] = $(this).data('datepickerDateformat');
        };
        if ( $(this).data('datepickerMindate') ) {
            options['minDate'] = $(this).data('datepickerMindate');
        };
        $(this).datepicker( "option", options );
        $(this).datepicker( "setDate", value );
    }

    $(document).on('ready',function(){
        $(".date").datepicker().each(initDatePicker);
    });

    $(document).on('opendialog',function(e, container){
        $(container).find('.date').datepicker().each(initDatePicker)
    });

})(jQuery);