var path = require("path");
var webpack = require("webpack");

var startsWith = function(str, searchString) {
    return str.lastIndexOf(searchString, 0) === 0;
};

function resolve(base) {
    return startsWith(base, "/") ? base : path.resolve(path.join(path.dirname(__filename), base));
}

function resolver(base) {
    return function(sub) {
        return resolve(base ? (sub ? path.join(resolve(base), sub) : resolve(base)) : sub ? resolve(sub) : __dirname);
    };
}

var JQUERY_TMPL = resolver("../node-modules/jquery-tmpl");
var JQUERY_BASE = resolver("../node-modules/jquery");
var LOGGING = resolver("../node_modules/logging");
var MOCKUP = resolver("../node_modules/mockup/mockup");
var MOCKUP_CORE = resolver("../node_modules/mockup-core");
var PATTERNSLIB = resolver("../node_modules/patternslib");
var TINYMCE = resolver("../node_modules/tinymce");
var ACEMOD = resolver("../node_modules/ace-editor-builds/src");
var APP_SCRIPTS = resolver("../app/assets/scripts");
var PLOMINO = resolver("../../src/Products/CMFPlomino/browser/static/js");

var alias = {
    // Legacy bower aliases
    bowerbootstrap: "bootstrap",
    "bower/bootstrap": "bootstrap",
    "bower/dropzone": "dropzone",
    "bower/jqtree": "jqtree",
    "bower/pickadate": "pickadate",
    "bower/select2": "select2",
    "bower/tinymce-builded": TINYMCE(),

    // Plone core-bundles and mockup aliases
    // 'jquery': JQUERY_BASE('dist/jquery'),
    // 'plomino-dynamic': PLOMINO('dynamic'),
    // 'plomino-formula': PLOMINO('formula'),

    // 'ace': ACEMOD('ace'),
    ace: "ace",
    // 'ace/mode/javascript': ACEMOD('mode-javascript'),
    // 'ace/mode/text': ACEMOD('mode-text'),
    // 'ace/mode/css': ACEMOD('mode-css'),
    // 'ace/mode/html': ACEMOD('mode-html'),
    // 'ace/mode/xml': ACEMOD('mode-xml'),
    // 'ace/mode/less': ACEMOD('mode-less'),
    // 'ace/mode/python': ACEMOD('mode-python'),
    // 'ace/mode/ini': ACEMOD('mode-ini'),
    "bootstrap-alert": "bootstrap/js/alert",
    "bootstrap-collapse": "bootstrap/js/collapse",
    "bootstrap-dropdown": "bootstrap/js/dropdown",
    "bootstrap-tooltip": "bootstrap/js/tooltip",
    "bootstrap-transition": "bootstrap/js/transition",
    "jquery.event.drag": MOCKUP("lib/jquery.event.drag"),
    "jquery.event.drop": MOCKUP("lib/jquery.event.drop"),
    "jquery.form": "jquery-form",
    "jquery.tmpl": JQUERY_TMPL("jquery.tmpl"),
    "mockup-i18n": MOCKUP("js/i18n"),
    "mockup-less": MOCKUP("less"),
    mockup: MOCKUP("patterns"),
    "mockup-parser": MOCKUP_CORE("js/parser"),
    "mockup-registry": MOCKUP_CORE("js/registry"),
    "mockup-patterns-autotoc.less": MOCKUP("patterns/autotoc/pattern.autotoc.less"),
    "mockup-patterns-autotoc": MOCKUP("patterns/autotoc/pattern"),
    "mockup-patterns-backdrop": MOCKUP("patterns/backdrop/pattern"),
    "mockup-patterns-base": MOCKUP_CORE("js/pattern"),
    "mockup-patterns-contentloader": MOCKUP("patterns/contentloader/pattern"),
    "mockup-patterns-cookietrigger": MOCKUP("patterns/cookietrigger/pattern"),
    "mockup-patterns-eventedit": MOCKUP("patterns/eventedit/pattern"),
    "mockup-patterns-filemanager": MOCKUP("patterns/filemanager/pattern"),
    "mockup-patterns-filemanager.less": MOCKUP("patterns/filemanager/pattern.filemanager.less"),
    "mockup-patterns-filemanager-url": MOCKUP("patterns/filemanager"),
    "mockup-patterns-formautofocus": MOCKUP("patterns/formautofocus/pattern"),
    "mockup-patterns-formunloadalert": MOCKUP("patterns/formunloadalert/pattern"),
    "mockup-patterns-inlinevalidation": MOCKUP("patterns/inlinevalidation/pattern"),
    "mockup-patterns-livesearch.less": MOCKUP("patterns/livesearch/pattern.livesearch.less"),
    "mockup-patterns-livesearch": MOCKUP("patterns/livesearch/pattern"),
    "mockup-patterns-markspeciallinks.less": MOCKUP("patterns/markspeciallinks/pattern.markspeciallinks.less"),
    "mockup-patterns-markspeciallinks": MOCKUP("patterns/markspeciallinks/pattern"),
    "mockup-patterns-modal.less": MOCKUP("patterns/modal/pattern.modal.less"),
    "mockup-patterns-modal": APP_SCRIPTS("modal-pattern"),
    "mockup-patterns-moment": MOCKUP("patterns/moment/pattern"),
    "mockup-patterns-passwordstrength": MOCKUP("patterns/passwordstrength/pattern"),
    "mockup-patterns-passwordstrength-url": MOCKUP("patterns/passwordstrength"),
    "mockup-patterns-pickadate.less": MOCKUP("patterns/pickadate/pattern.pickadate.less"),
    "mockup-patterns-pickadate": MOCKUP("patterns/pickadate/pattern"),
    "mockup-patterns-preventdoublesubmit": MOCKUP("patterns/preventdoublesubmit/pattern"),
    "mockup-patterns-querystring.less": MOCKUP("patterns/querystring/pattern.querystring.less"),
    "mockup-patterns-querystring": MOCKUP("patterns/querystring/pattern"),
    "mockup-patterns-recurrence.less": MOCKUP("patterns/recurrence/pattern.recurrence.less"),
    "mockup-patterns-recurrence": MOCKUP("patterns/recurrence/pattern"),
    "mockup-patterns-relateditems.less": MOCKUP("patterns/relateditems/pattern.relateditems.less"),
    "mockup-patterns-relateditems": MOCKUP("patterns/relateditems/pattern"),
    "mockup-patterns-resourceregistry": MOCKUP("patterns/resourceregistry/pattern"),
    "mockup-patterns-resourceregistry.less": MOCKUP("patterns/resourceregistry/pattern.resourceregistry.less"),
    "mockup-patterns-resourceregistry-url": MOCKUP("patterns/resourceregistry"),
    "mockup-patterns-select2.less": MOCKUP("patterns/select2/pattern.select2.less"),
    "mockup-patterns-select2": MOCKUP("patterns/select2/pattern"),
    "mockup-patterns-sortable": MOCKUP("patterns/sortable/pattern"),
    "mockup-patterns-structure.less": MOCKUP("patterns/structure/less/pattern.structure.less"),
    "mockup-patterns-structure": MOCKUP("patterns/structure/pattern"),
    "mockup-patterns-structure-url": MOCKUP("patterns/structure"),
    "mockup-patterns-textareamimetypeselector": MOCKUP("patterns/textareamimetypeselector/pattern"),
    "mockup-patterns-texteditor": MOCKUP("patterns/texteditor/pattern"),
    "mockup-patterns-thememapper": MOCKUP("patterns/thememapper/pattern"),
    "mockup-patterns-thememapper.less": MOCKUP("patterns/thememapper/pattern.thememapper.less"),
    "mockup-patterns-thememapper-url": MOCKUP("patterns/thememapper"),
    "mockup-patterns-tinymce.less": MOCKUP("patterns/tinymce/less/pattern.tinymce.less"),
    "mockup-patterns-tinymce": MOCKUP("patterns/tinymce/pattern"),
    "mockup-patterns-tinymce-links": MOCKUP("patterns/tinymce/js/links"),
    "mockup-patterns-tinymce-url": MOCKUP("patterns/tinymce"),
    "mockup-patterns-toggle": MOCKUP("patterns/toggle/pattern"),
    "mockup-patterns-tooltip": MOCKUP("patterns/tooltip/pattern"),
    "mockup-patterns-tree": MOCKUP("patterns/tree/pattern"),
    "mockup-patterns-upload.less": MOCKUP("patterns/upload/less/pattern.upload.less"),
    "mockup-patterns-upload": MOCKUP("patterns/upload/pattern"),
    "mockup-patterns-upload-url": MOCKUP("patterns/upload"),
    "mockup-router": MOCKUP("js/router"),
    "mockup-ui-url": MOCKUP("js/ui"),
    "mockup-utils": MOCKUP("js/utils"),
    "picker.date": "pickadate/lib/picker.date",
    picker: "pickadate/lib/picker",
    "picker.time": "pickadate/lib/picker.time",
    translate: MOCKUP("js/i18n-wrapper"),

    // TinyMCE aliases
    "tinymce-advlist": TINYMCE("js/tinymce/plugins/advlist/plugin"),
    "tinymce-anchor": TINYMCE("js/tinymce/plugins/anchor/plugin"),
    "tinymce-autolink": TINYMCE("js/tinymce/plugins/autolink/plugin"),
    "tinymce-autoresize": TINYMCE("js/tinymce/plugins/autoresize/plugin"),
    "tinymce-autosave": TINYMCE("js/tinymce/plugins/autosave/plugin"),
    "tinymce-bbcode": TINYMCE("js/tinymce/plugins/bbcode/plugin"),
    "tinymce-charmap": TINYMCE("js/tinymce/plugins/charmap/plugin"),
    "tinymce-code": TINYMCE("js/tinymce/plugins/code/plugin"),
    "tinymce-colorpicker": TINYMCE("js/tinymce/plugins/colorpicker/plugin"),
    "tinymce-compat3x": TINYMCE("js/tinymce/plugins/compat3x/plugin"),
    "tinymce-contextmenu": TINYMCE("js/tinymce/plugins/contextmenu/plugin"),
    "tinymce-directionality": TINYMCE("js/tinymce/plugins/directionality/plugin"),
    "tinymce-emoticons": TINYMCE("js/tinymce/plugins/emoticons/plugin"),
    "tinymce-fullpage": TINYMCE("js/tinymce/plugins/fullpage/plugin"),
    "tinymce-fullscreen": TINYMCE("js/tinymce/plugins/fullscreen/plugin"),
    "tinymce-hr": TINYMCE("js/tinymce/plugins/hr/plugin"),
    "tinymce-image": TINYMCE("js/tinymce/plugins/image/plugin"),
    "tinymce-importcss": TINYMCE("js/tinymce/plugins/importcss/plugin"),
    "tinymce-insertdatetime": TINYMCE("js/tinymce/plugins/insertdatetime/plugin"),
    "tinymce-layer": TINYMCE("js/tinymce/plugins/layer/plugin"),
    "tinymce-legacyoutput": TINYMCE("js/tinymce/plugins/legacyoutput/plugin"),
    "tinymce-link": TINYMCE("js/tinymce/plugins/link/plugin"),
    "tinymce-lists": TINYMCE("js/tinymce/plugins/lists/plugin"),
    "tinymce-media": TINYMCE("js/tinymce/plugins/media/plugin"),
    "tinymce-modern-theme": TINYMCE("js/tinymce/themes/modern/theme"),
    "tinymce-nonbreaking": TINYMCE("js/tinymce/plugins/nonbreaking/plugin"),
    "tinymce-noneditable": TINYMCE("js/tinymce/plugins/noneditable/plugin"),
    "tinymce-pagebreak": TINYMCE("js/tinymce/plugins/pagebreak/plugin"),
    "tinymce-paste": TINYMCE("js/tinymce/plugins/paste/plugin"),
    "tinymce-preview": TINYMCE("js/tinymce/plugins/preview/plugin"),
    "tinymce-print": TINYMCE("js/tinymce/plugins/print/plugin"),
    "tinymce-save": TINYMCE("js/tinymce/plugins/save/plugin"),
    "tinymce-searchreplace": TINYMCE("js/tinymce/plugins/searchreplace/plugin"),
    "tinymce-spellchecker": TINYMCE("js/tinymce/plugins/spellchecker/plugin"),
    "tinymce-tabfocus": TINYMCE("js/tinymce/plugins/tabfocus/plugin"),
    "tinymce-table": TINYMCE("js/tinymce/plugins/table/plugin"),
    "tinymce-template": TINYMCE("js/tinymce/plugins/template/plugin"),
    "tinymce-textcolor": TINYMCE("js/tinymce/plugins/textcolor/plugin"),
    "tinymce-textpattern": TINYMCE("js/tinymce/plugins/textpattern/plugin"),
    "tinymce-visualblocks": TINYMCE("js/tinymce/plugins/visualblocks/plugin"),
    "tinymce-visualchars": TINYMCE("js/tinymce/plugins/visualchars/plugin"),
    "tinymce-wordcount": TINYMCE("js/tinymce/plugins/wordcount/plugin"),
    "tinymce/skins": TINYMCE("js/tinymce/skins"),
    "tinymce/plugins": TINYMCE("js/tinymce/plugins"),
    "tinymce/themes": TINYMCE("js/tinymce/themes"),
    tinymce: TINYMCE("js/tinymce/tinymce"),

    // Patternslib aliases
    patternslib: PATTERNSLIB("src/"),
    "pat-base": PATTERNSLIB("src/core/base"),
    "pat-compat": PATTERNSLIB("/src/core/compat"),
    "pat-jquery-ext": PATTERNSLIB("src/core/jquery-ext"),
    "pat-logger": PATTERNSLIB("/src/core/logger"),
    "pat-mockup-parser": PATTERNSLIB("src/core/mockup-parser"),
    "pat-registry": PATTERNSLIB("src/core/registry"),
    "pat-utils": PATTERNSLIB("src/core/utils"),
    logging: LOGGING("src/logging"),
};

function AddToContextPlugin(condition, extras) {
    this.condition = condition;
    this.extras = extras || [];
}

// http://stackoverflow.com/questions/30065018/
// dynamically-require-an-aliased-module-using-webpack
AddToContextPlugin.prototype.apply = function(compiler) {
    var condition = this.condition;
    var extras = this.extras;
    var newContext = false;
    compiler.plugin("context-module-factory", function(cmf) {
        cmf.plugin("after-resolve", function(items, callback) {
            newContext = true;
            return callback(null, items);
        });
        // this method is called for every path in the ctx
        // we just add our extras the first call
        cmf.plugin("alternatives", function(items, callback) {
            if (newContext && items[0].context.match(condition)) {
                newContext = false;
                var alternatives = extras.map(function(extra) {
                    return {
                        context: items[0].context,
                        request: extra,
                    };
                });
                items.push.apply(items, alternatives);
            }
            return callback(null, items);
        });
    });
};

module.exports = {
    resolve: {
        alias: alias,
    },
    module: {
        loaders: [
            { test: alias["tinymce"], loader: "imports?document=>window.document,this=>window!exports?window.tinymce" },

            { test: /tinymce\/plugins/, loader: "imports?tinymce,this=>{tinymce:tinymce}" },

            { test: alias["jquery.event.drop"], loader: "exports?$.drop" },

            { test: /backbone\.paginator/, loader: "imports?_=underscore" },

            {
                test: alias["mockup-patterns-texteditor"],
                loader:
                    "imports?ace=ace,_a=ace/mode/javascript,_b=ace/mode/text,_c=ace/mode/css,_d=ace/mode/html,_e=ace/mode/xml,_f=ace/mode/less,_g=ace/mode/python,_h=ace/mode/xml,_i=ace/mode/ini",
            },
        ],
    },
};
