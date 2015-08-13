tinymce.PluginManager.add('plomino', function(editor, url) {
    var isNotFormEditor = !$('body').hasClass('portaltype-plominoform');

    if (isNotFormEditor) {
        return ;
    }

    // Add a button that opens a window
    editor.addButton('plominofield', {
        image: '++resource++Products.CMFPlomino/img/PlominoField.png',
        onclick: function () {console.log('TODO')}
    });
    editor.addButton('plominoaction', {
        image: '++resource++Products.CMFPlomino/img/PlominoAction.png',
        onclick: function () {console.log('TODO')}
    });
    editor.addButton('plominosubform', {
        image: '++resource++Products.CMFPlomino/img/PlominoForm.png',
        onclick: function () {console.log('TODO')}
    });
    editor.addButton('plominohidewhen', {
        image: '++resource++Products.CMFPlomino/img/PlominoHideWhen.png',
        onclick: function () {console.log('TODO')}
    });
    editor.addButton('plominocache', {
        image: '++resource++Products.CMFPlomino/img/PlominoCache.png',
        onclick: function () {console.log('TODO')}
    });

});