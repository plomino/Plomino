function update(obj/*, …*/) {
    for (var i=1; i<arguments.length; i++) {
        for (var prop in arguments[i]) {
            var val = arguments[i][prop];
            if (typeof val == "object") // this also applies to arrays or null!
                update(obj[prop], val);
            else
                obj[prop] = val;
        };
    };
    return obj;
};

$(document).ready(function() {
    //datepicker widget
    $(".date").datepicker().each(function(){
        var value = $(this).val();
        eval("var options = "  + $(this).data('datepickerOptions')+" ||{}");
        if ($(this).data('datepickerDateformat')&&!('dateFormat' in options)) {
            // in case you use unusual date format not easily convertible between jQuery dateFormat and python
            options['dateFormat'] = $(this).data('datepickerDateformat');
        };
        if ( $(this).data('datepickerMindate') ) {
            options['minDate'] = $(this).data('datepickerMindate');
        };
        console.log(options);
        $(this).datepicker( "option", options );
        $(this).datepicker( "setDate", value );
        $('#btn_' + this.id).click(function() {
            $(this).datepicker('show');
        });
    });
});
