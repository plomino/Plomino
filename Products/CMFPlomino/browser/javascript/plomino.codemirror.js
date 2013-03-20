$(document).ready(function() {
	plomino_types = ['plominoaction',
	                 'plominoagent',
	                 'plominocache',
	                 'plominocolumn',
	                 'plominohidewhen',
	                 'plominofield',
	                 'plominoview'];
	$(plomino_types).each(function(index, type) {
		$("#"+type+"-base-edit textarea").each(function() {
			this.onCodeMirrorSave = function() { 
				$("#"+type+"-base-edit").submit();
			};
			$(this).addClass('codemirror-python')
			$(this).attr('data-codemirror-mode', "python");
		});
	});
	
	// enable on all PlominoField settings page
	// TODO: SAVE
	$(".portaltype-plominofield #content-core textarea").each(function() {
		this.onCodeMirrorSave = function() {
			$("input[name='form.actions.apply']").click();
		};
		$(this).addClass('codemirror-python');
		$(this).attr('data-codemirror-mode', "python");
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
	                      'beforeCreateDocument',
	                      'beforeSaveDocument'
	                      ]
	$(plomino_form_areas).each(function(index, area) {
		$("#plominoform-base-edit #"+area).each(function() {
			this.onCodeMirrorSave = function() { 
				$("#plominoform-base-edit").submit();
			};
			$(this).addClass('codemirror-python');
			$(this).attr('data-codemirror-mode', "python");
		});
	});
});