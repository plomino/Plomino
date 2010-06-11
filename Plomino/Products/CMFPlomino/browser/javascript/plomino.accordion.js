$(document).ready(function() {
	// Declare accordions and sub-accordions
	$("#plomino_form h6.plomino-accordion-header").parent().accordion({
		header: "h6.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	$("#plomino_form h5.plomino-accordion-header").parent().accordion({
		header: "h5.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	$("#plomino_form h4.plomino-accordion-header").parent().accordion({
		header: "h4.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	$("#plomino_form h3.plomino-accordion-header").parent().accordion({
		header: "h3.plomino-accordion-header", collapsible: true, autoHeight: false
	});
});
