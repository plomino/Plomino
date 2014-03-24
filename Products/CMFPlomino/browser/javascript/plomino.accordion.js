$(document).ready(function() {
	// Declare accordions and sub-accordions
	$("h6.plomino-accordion-header").parent().accordion({
		header: "h6.plomino-accordion-header", active: false, collapsible: true, autoHeight: false
	});
	$("h5.plomino-accordion-header").parent().accordion({
		header: "h5.plomino-accordion-header", active: false, collapsible: true, autoHeight: false
	});
	$("h4.plomino-accordion-header").parent().accordion({
		header: "h4.plomino-accordion-header", active: false, collapsible: true, autoHeight: false
	});
	$("h3.plomino-accordion-header").parent().accordion({
		header: "h3.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	
	$(".plomino-accordion-header").click(function(e) {
        url = $(this).find("a").attr("href");
        if(url!="#") {
           var contentDiv = $(this).next("div");
           contentDiv.load($(this).find("a").attr("href")+" #content");
           $(this).find("a").attr("href", "#");
        }
    });
});
