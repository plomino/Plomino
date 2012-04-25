jq(document).ready(function() {
	plomino_types = ['plominoaction',
	                 'plominoagent',
	                 'plominocache',
	                 'plominocolumn',
	                 'plominohidewhen',
	                 'plominofield',
	                 'plominoview'];
	jq(plomino_types).each(function(index, type) {
		jq("#"+type+"-base-edit textarea").each(function() {
			this.onCodeMirrorSave = function() { 
				jq("#"+type+"-base-edit").submit();
			};
			jq(this).addClass('codemirror-python')
			jq(this).attr('data-codemirror-mode', "python");
		});
	});
	
	// enable on all PlominoField settings page
	// TODO: SAVE
	jq(".portaltype-plominofield #content-core textarea").each(function() {
		this.onCodeMirrorSave = function() {
			alert("Ctrl+S not implemented here.");
		};
		jq(this).addClass('codemirror-python');
		jq(this).attr('data-codemirror-mode', "python");
	});

	// plominoform textareas must be processed more precisely
	plomino_form_areas = ['DocumentTitle',
	                      'DocumentId',
	                      'SearchFormula',
	                      'onCreateDocument',
	                      'onOpenDocument',
	                      'onSaveDocument',
	                      'onDeleteDocument',
	                      'onSearch',
	                      'beforeCreateDocument'
	                      ]
	jq(plomino_form_areas).each(function(index, area) {
		jq("#plominoform-base-edit #"+area).each(function() {
			this.onCodeMirrorSave = function() { 
				jq("#plominoform-base-edit").submit();
			};
			jq(this).addClass('codemirror-python');
			jq(this).attr('data-codemirror-mode', "python");
		});
	});
});