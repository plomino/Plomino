function debug_plomino(context, formula_path) {
	content_node = document.getElementById("content-core")
	if (content_node == null) {
		// preserve compatibility with Plone 3
		content_node = document.getElementById("region-content")
	}
	if (content_node == null) {
		// in case the skin is missing those 2 ids, we default to 'content'
		content_node = document.getElementById("content")
	}
    var footer = content_node.nextSibling;
    var wrapper = content_node.parentNode;
    
    var div = document.createElement("div");
    var iframe = document.createElement("iframe");
    
    var existing = document.getElementById("clouseau_iframe");
    if (existing) {
    	session_id = jq("#clouseau_iframe iframe").contents().find("#session-id").text();
    	jq.get("./clouseau_tool/stop_session?session_id="+session_id, function(data) {
    		jq('#clouseau_iframe').remove();
    	});

    } else {
        // else lets build it
        div.id = "clouseau_iframe";

        iframe.src = "clouseau_plomino?formula="+ formula_path +"&context=" + context;
        iframe.style.width = "100%";
        iframe.style.height = "800px";
        div.appendChild(iframe);

        wrapper.insertBefore(div, footer);
        wrapper.focus();
    }
}

function init_debugger() {
	debug_row = "<tr id='debug' class='output-row'><td class='output-cell'><span class='ui-state-highlight' id='debug-button'><a href='javascript:start_debug()' title='Start debugging' class='ui-icon ui-icon-circle-triangle-e'>Debug</a></span></td><td class='output-cell'></td><td class='output-cell'><code id='debug-code'>Start debugging Plomino formula...</code></td></tr>"
    jq(debug_row).insertAfter(".border");
}

function start_debug() {
	eval_codeline("plominoContext = context");
    eval_codeline("plominoDocument = context");
    eval_codeline("from Products.CMFPlomino.PlominoUtils import DateToString, StringToDate, DateRange, sendMail, userFullname, userInfo, htmlencode, Now, asList, urlencode, csv_to_array, MissingValue, open_url, asUnicode, array_to_csv");
    //jq("#debug-button").remove();
    jq("#debug-button").html("<a href='javascript:execute_next()' title='Next' class='ui-icon ui-icon-circle-triangle-e'>Debug</a>");
    jq('#debug-code').text(formula_lines[current_line]);
}

function stop_debug() {
	jq.get("./clouseau_tool/stop_session?session_id="+_session_id, function(data) {
		jq(window.parent.document).find('#clouseau_iframe').remove();
	});
}
function execute_next() {
	eval_codeline(formula_lines[current_line]);
	current_line = current_line + 1;
	if(current_line < formula_lines.length) {
		line = formula_lines[current_line];
		//TODO: replace indent with dots
		jq('#debug-code').text(line);
	} else {
		jq('#debug-code').text('[end]');
		jq("#debug-button").html("<a href='javascript:stop_debug()' title='Stop debugging' class='ui-icon ui-icon-circle-close'>Stop</a>");
	}
}

function eval_codeline(line) {
	line = line.replace("return ", "");
    var f_input = jq("#input-field");
    //f_input.val(line).focus();
    f_input.val(line);
    e = jQuery.Event("keyup");
    e.keyCode = jq.ui.keyCode.ENTER;
    inputKeyup(e);
    jq("#debug-button").focus();
}