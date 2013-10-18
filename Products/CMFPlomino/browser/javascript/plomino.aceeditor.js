$(document).ready(function() {
    
    var plomino_types = [   
                            'plominoaction',
                            'plominoagent',
                            'plominocache',
                            'plominocolumn',
                            'plominohidewhen',
                            'plominofield',
                            'plominoview'
                        ];

    var plomino_form_areas = [  
                                'DocumentTitle',
                                'DocumentId',
                                'SearchFormula',
                                'onCreateDocument',
                                'onOpenDocument',
                                'onSaveDocument',
                                'onDeleteDocument',
                                'onSearch',
                                'beforeCreateDocument',
                                'beforeSaveDocument'
                            ];

    var dom = require("ace/lib/dom")
    var commands = require("ace/commands/default_commands").commands

    commands.push({
            name: "Toggle Fullscreen",
            bindKey: "F11",
            exec: function(editor) {
                dom.toggleCssClass(document.body, "ace-fullscreen")
                dom.toggleCssClass(editor.container, "ace-fullscreen-editor")
                editor.resize()
            }
    })

    commands.push({
            name: 'Save',
            bindKey: {
                win: 'Ctrl-S',
                mac: 'Command-S',
                sender: 'editor|cli'
            },
            exec: function(editor) {
                $(editor.container).parents("form")[0].submit();
            }
    });

    $(jQuery.merge(plomino_types,plomino_form_areas)).each(function(index, type) {
        
        $("#"+type+"-base-edit textarea,#plominoform-base-edit #"+type).each(function(i,textarea) {
            var editor, 
                session,
                $textarea, 
                $container, 
                $switcher, 
                $checkbox;          

            $textarea = $(textarea);

            // disable textarea #Formula for user role designer
            if( $('.userrole-plominodesigner').length > 0 ) {
                $textarea.prop('disabled', true);
            }
            else {
                // current size
                var width = $textarea.width();
                var height = $textarea.height();

                // Create container that we will use to plug ace editor
                $container = $('<div/>')
                                        .css({
                                            position: 'relative',
                                            width: width,
                                            height: height
                                            })
                                        .insertAfter(textarea);

                // Hide plone useless functionality on Page 
                $("#"+$textarea.attr("id")+"_text_format").parent().hide();

                $textarea.hide();

                // Create checkbox to switch between ace/raw textarea **/
                $switcher = $("<span/>").insertBefore($textarea);
                $checkbox = $("<input type='checkbox' checked/>")
                $switcher.append($checkbox)
                         .append($("<label/>").text("Ace"));
                
                /**
                    Ace Editor Configuration
                **/

                editor = ace.edit($container[0]);
                editor.setShowPrintMargin(false);
                //editor.setTheme("ace/theme/eclipse")
                toggleFocus(editor)

                session = editor.getSession();
                session.setValue( $textarea.val());
                session.setUseWrapMode(true);
                session.setMode('ace/mode/python');

                /** resizable / Jquery UI **/
                
                $container.resizable({ 
                            maxWidth: $container.width(), 
                            minWidth: $container.width(),
                            resize: function(event){ editor.resize() } 
                        });

                /** 
                    Events 
                **/

                session.on('change', function () {
                    $textarea.val(session.getValue());
                });

                editor.on("blur",function(e){
                    toggleFocus(editor);
                })

                editor.on("focus",function(e){
                    toggleFocus(editor);
                })

                $textarea.change(function () {
                    session.setValue($textarea.val());
                })

                $checkbox.change(function(e){
                    $container.toggle();
                    $textarea.toggle();
                });
            }
        });
    });

    function toggleFocus(editor,activate) {
        var activate = activate | !editor.getHighlightActiveLine()
        editor.setShowInvisibles(activate)
        editor.setHighlightActiveLine(activate);
        editor.setHighlightGutterLine(activate);
    }
});
