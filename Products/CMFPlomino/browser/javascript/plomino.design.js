/** Selector extension **/
$.extend($.expr[':'].icontains = function(a, i, m) {
        var sText   = (a.textContent || a.innerText || "");
        var zRegExp = new RegExp (m[3], 'i');
        return zRegExp.test (sText);
   }
);

function databaseDesign_filtering() {
    var $design_fields = $("span.field");
    var $design_agents = $("ul.agents li");
    var $design_autocomplete = $("#autocomplete_database_design");
    var $elements = $("#content .field,#content .collapsibleHeader");
    var $expendables = $(".expandable");
    //Tip
    $design_fields.css("font-weight","normal");

    /** KeyUp event on autocomplete input **/
    $("#autocomplete_database_design").keyup(
        function ( event ) {
            //var beginning = (new Date).getTime();
            var value = $(this).val();
            $(".partTree.collapsedInlineCollapsible>dt.collapsibleHeader").click();
            if ( ( value !== "" ) && ( value.length > 1 ) ) {
                /** Reset elements **/
                $design_fields.css("font-weight","normal");
                $expendables.hide();
                $design_agents.hide();

                /** Show filtered elements **/
                $elements.filter(":icontains('"+value+"')").parents(".expandable:hidden").show();
                $design_fields.filter(":icontains('"+value+"')").css("font-weight","bold");
                $design_agents.filter(":icontains('"+value+"')").show();
            }
            else {
                /** Show all elements**/
                $(".partTree .expandable").show();
            }
            //     var endtime=(new Date).getTime();
            //     console.log("timer : " + (endtime - beginning) );
        }
    );

    /** Activate filter if autocomplete input is not empty **/
    if ( $design_autocomplete.val().length > 0 ) {
        $design_autocomplete.keyup();
    }
}