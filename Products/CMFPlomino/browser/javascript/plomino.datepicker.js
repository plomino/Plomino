$(document).ready(function() {
    //datepicker widget
    $(".date").datepicker().each(function(){
        eval("var options = "  + $(this).data('datepickerOptions')+"||{}");
        $(this).datepicker( "option", options );
        $('#btn_' + this.id).click(function() {
            $(this).datepicker('show');
        });
    });
});
