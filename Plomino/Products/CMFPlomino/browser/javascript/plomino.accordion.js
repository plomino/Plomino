jq(document).ready(function() {
	// Declare accordions and sub-accordions
	jq("h6.plomino-accordion-header").parent().accordion({
		header: "h6.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	jq("h5.plomino-accordion-header").parent().accordion({
		header: "h5.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	jq("h4.plomino-accordion-header").parent().accordion({
		header: "h4.plomino-accordion-header", collapsible: true, autoHeight: false
	});
	jq("h3.plomino-accordion-header").parent().accordion({
		header: "h3.plomino-accordion-header", collapsible: true, autoHeight: false
	});
});
